print("Importing modules...")
# ML imports
from cv2 import cvtColor, COLOR_BGR2RGB
from imageai.Detection import ObjectDetection
from requests import get
from os import path
from playsound import playsound

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
MAX = 3

class CameraMonitor:
    def __init__(self):
        self.is_playing = False
        self.initialiseDetector()
        self.initialiseWindow()
        self.serialConfig()
        self.window.mainloop()

        self.port.close()
        exit(0)


    def initialiseDetector(self):
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

        self.count = 0


    def initialiseWindow(self):
        # Open tkinter window
        self.window = Tk()  
        self.window.title('Door Monitor')
        self.window.geometry(f'{WIDTH}x{HEIGHT}')

        # Create initial image
        tkImage = ImageTk.PhotoImage(Image.open("Start.jpg"))
        self.panel = Label(self.window, image = tkImage)
        self.panel.grid(column=1, row=1)

        self.counter = Label(self.window, text="Total: 0", fg="green", font=("Roboto Mono Bold", 20), justify="left")
        self.counter.place(x=60, y=20, anchor='n')
        self.window.update()


    def serialConfig(self):
        # Bind mouse click to start monitoring
        self.window.bind("<Button-1>", self.click)

        # Configure serial port
        self.port = Serial('/dev/tty.SLAB_USBtoUART', baudrate=BAUDRATE, timeout=3)
        self.port.flush()


    def click(self, event):
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
        image.save("temp.jpg")


    def updateImage(self):
        # Copy temp image to detector image
        copyfile("temp.jpg", "detect.jpg")

        # Start loading next image
        process = Thread(target=self.newImage)
        process.start()

        # Detect people in current image
        image = self.detectPeople("detect.jpg")

        # Update image in window
        tkImage = ImageTk.PhotoImage(image)
        self.panel.destroy()
        self.panel = Label(self.window, image = tkImage)
        self.panel.grid(column=1, row=1)

        #Update counter
        self.counter.destroy()
        if(self.count >= MAX):
            colour = "red"
            if self.is_playing == False:
                self.is_playing = True
                sound = Thread(target=self.play)
                sound.start()
        else:
            self.is_playing = False
            colour = "green"
        self.counter = Label(self.window, text="Total: "+str(self.count), fg=colour, font=("Roboto Mono Bold", 20), justify="left")
        self.counter.place(x=60, y=20, anchor='n')
        self.window.update()
        print(self.count)

        # Wait until next image loaded
        process.join()
        self.window.after(0, self.updateImage)


    def detectPeople(self, filename):
        print("Detecting people in image...")

        # Detect people in image
        peopleOnly = self.detector.CustomObjects(person=True)
        image, detections = self.detector.detectObjectsFromImage(custom_objects=peopleOnly, output_type="array", input_image=filename, minimum_percentage_probability=70)
        self.count = len(detections)

        # Convert image back to PIL and return
        image = cvtColor(image, COLOR_BGR2RGB)
        return Image.fromarray(image)


    def play(self):
        playsound('military-alarm-129017.mp3')

if __name__ == "__main__":
    print("Starting program...")

    monitor = CameraMonitor()