print("Importing modules...")
# ML imports
from cv2 import cvtColor, COLOR_RGB2BGR, COLOR_BGR2RGB
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
import numpy as np

def mlConfig():
    global detector

    # Load yolo.h5 model
    if not path.exists('../yolo.h5'):
        r = get(modelYOLOv3, timeout=0.5)
        with open('../yolo.h5', 'wb') as outfile:
            outfile.write(r.content)

    # Initialise object detection
    detector = ObjectDetection()
    detector.setModelTypeAsYOLOv3()
    detector.setModelPath('../yolo.h5')
    detector.loadModel()

def serialConfig():
    global port

    # Bind mouse click to start monitoring
    window.bind("<Button-1>", click)

    # Configure serial port
    port = Serial('/dev/tty.SLAB_USBtoUART', baudrate=BAUDRATE)
    port.flush()

def click(event):
    updateImage()

def detectPeople(filename):
    print("Detecting people in image...")

    # Detect people in image
    peopleOnly = detector.CustomObjects(person=True)
    image, detections = detector.detectObjectsFromImage(custom_objects=peopleOnly, output_type="array", input_image=filename, minimum_percentage_probability=30)

    # Convert image back to PIL and return
    image = cvtColor(image, COLOR_BGR2RGB)
    return Image.fromarray(image)

def updateImage():
    global panel
    print("Processing next image...")

    # Message spresence to capture next image
    port.write('S'.encode())
    sleep(0.01)

    # Get the number of bytes for the image
    message = port.readline()
    message = str(message, "UTF-8")

    # Read the image over serial
    bytes_read = port.read(int(message))

    # Reconstruct the image from the received data
    image = Image.open(BytesIO(bytes_read))
    image.save("temp.jpg")
    image = detectPeople("temp.jpg")

    # Update image in window
    tkImage = ImageTk.PhotoImage(image)
    panel.destroy()
    panel = Label(window, image = tkImage)
    panel.grid(column=1, row=1)
    window.update()

    window.after(0, updateImage)


print("Starting program...")

# Static ML variables
modelRetinaNet = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/resnet50_coco_best_v2.0.1.h5'
modelYOLOv3 = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo.h5'
modelTinyYOLOv3 = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo-tiny.h5'

# Static spresence variables
BAUDRATE = 2000000
WIDTH = int(1280/2)
HEIGHT = int(960/2)

mlConfig()

# Open tkinter window
window = Tk()  
window.title('Door Monitor')
window.geometry(f'{WIDTH}x{HEIGHT}')

# Create initial image
tkImage = ImageTk.PhotoImage(Image.open("Start.jpg"))
panel = Label(window, image = tkImage)
panel.grid(column=1, row=1)
window.update()

serialConfig()
window.mainloop()

port.close()
exit(0)

# for eachObject in detections:
#     print(eachObject["name"] , " : ", eachObject["percentage_probability"], " : ", eachObject["box_points"] )
#     print("--------------------------------")