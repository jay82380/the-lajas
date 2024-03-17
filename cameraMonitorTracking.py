print("Importing modules...")
# ML imports
from cv2 import cvtColor, COLOR_BGR2RGB, TrackerKCF_create, imread, rectangle
from imageai.Detection import ObjectDetection
from requests import get
from os import path

# Spresence imports
from serial import Serial
from io import BytesIO
from sys import exit
from tkinter import *
from PIL import ImageTk,Image
from time import sleep
from threading import Thread
from shutil import copyfile

# Static ML variables
modelRetinaNet = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/resnet50_coco_best_v2.0.1.h5'
modelYOLOv3 = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo.h5'
modelTinyYOLOv3 = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo-tiny.h5'
modelPath = '../yolo.h5'

# Static spresence variables
BAUDRATE = 2000000
WIDTH = int(1280/2)
HEIGHT = int(960/2)
TEMP = "temp.jpg"
DETECT = "detect.jpg"

class CameraMonitor:
    def __init__(self):
        self.initialiseWindow()
        self.serialConfig()
        self.window.mainloop()

        self.port.close()
        exit(0)


    def initialiseTracker(self):
        print("Initialising tracker...")
        # Load yolo.h5 model
        if not path.exists(modelPath):
            r = get(modelYOLOv3, timeout=0.5)
            with open(modelPath, 'wb') as outfile:
                outfile.write(r.content)

        # Initialise object detection
        self.detector = ObjectDetection()
        self.detector.setModelTypeAsYOLOv3()
        self.detector.setModelPath(modelPath)
        self.detector.loadModel(detection_speed="flash")
        self.peopleOnly = self.detector.CustomObjects(person=True)

        # Take first image and detect people
        self.newImage()
        image, detections = self.detector.detectObjectsFromImage(custom_objects=self.peopleOnly, output_type="array", input_image=TEMP, minimum_percentage_probability=50)

        # Display to monitor
        image = cvtColor(image, COLOR_BGR2RGB)
        Image.fromarray(image)
        self.showImage(image)

        # Initialise trackers for all people in image
        self.count = 0
        frame = imread(TEMP)
        self.trackers = []
        for detection in detections:
            x, y, w, h = detection['box_points']
            tracker = TrackerKCF_create()
            tracker.init(frame, (x, y, w, h))
            self.trackers.append(tracker)


    def initialiseWindow(self):
        # Open tkinter window
        self.window = Tk()  
        self.window.title('Door Monitor')
        self.window.geometry(f'{WIDTH}x{HEIGHT}')

        # Bind mouse click to start monitoring
        self.window.bind("<Button-1>", self.click)

        # Create initial image
        tkImage = ImageTk.PhotoImage(Image.open("Start.jpg"))
        self.panel = Label(self.window, image = tkImage)
        self.panel.grid(column=1, row=1)
        self.window.update()


    def serialConfig(self):
        # Configure serial port
        self.port = Serial('/dev/tty.SLAB_USBtoUART', baudrate=BAUDRATE, timeout=3)
        self.port.flush()


    def click(self, event):
        self.initialiseTracker()
        self.updateImage()


    def newImage(self):
        print(f"Processing next image...")
        # Message spresence to capture next image
        self.port.write('S'.encode())
        sleep(0.01)

        # Get the number of bytes for the image
        message = self.port.readline()
        message = str(message, "UTF-8")
        if(message == ''): print("SIZE TIMEOUT")

        # Read the image over serial
        bytes_read = self.port.read(int(message))
        if(len(bytes_read) < int(message)): print("IMAGE TIMEOUT")

        # Reconstruct the image from the received data
        image = Image.open(BytesIO(bytes_read))
        image.save(TEMP)


    def updateImage(self):
        # Copy temp image to detector image
        copyfile(TEMP, DETECT)

        # Start loading next image
        process = Thread(target=self.newImage)
        process.start()

        # Detect people in current image and display to window
        image = self.detectPeople(DETECT)
        self.showImage(image)

        # Wait until next image loaded
        process.join()
        self.window.after(0, self.updateImage)


    def showImage(self, image):
        print(self.count)
        # Update PIL image in window
        tkImage = ImageTk.PhotoImage(image)
        self.panel.destroy()
        self.panel = Label(self.window, image = tkImage)
        self.panel.grid(column=1, row=1)
        self.window.update()


    def detectPeople(self, filename):
        print("Detecting people in image...")

        # Tracking people in image
        frame = imread(filename)
        self.count = len(self.trackers)
        for tracker in self.trackers:
            success, bbox = tracker.update(frame)
            if success:
                x, y, w, h = [int(v) for v in bbox]
                rectangle(frame, (x, y), (x+w, y+h), (0,255,0),2)
            else:
                self.count -= 1

        # Convert image back to PIL and return
        image = cvtColor(frame, COLOR_BGR2RGB)
        return Image.fromarray(image)


if __name__ == "__main__":
    print("Starting program...")

    monitor = CameraMonitor()