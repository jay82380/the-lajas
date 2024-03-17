import serial
import io
import sys
from tkinter import *
from PIL import ImageTk,Image
from time import sleep

def configure():
    global port

    # Bind mouse click to start monitoring
    window.bind("<Button-1>", click)

    # Configure serial port
    port = serial.Serial('/dev/tty.SLAB_USBtoUART', baudrate=BAUDRATE)
    port.flush()

def click(event):
    updateImage()

def updateImage():
    global panel

    # Message spresence to capture next image
    port.write('S'.encode())
    sleep(0.01)

    # Get the number of bytes for the image
    # print("Reading the image...")
    message = port.readline()
    message = str(message, "UTF-8")
    # print(message)

    # Read the image over serial
    bytes_read = port.read(int(message))

    # Reconstruct the image from the received data
    # print(bytes_read)
    image = Image.open(io.BytesIO(bytes_read))
    tkImage = ImageTk.PhotoImage(image)
  
    # Update image in window
    panel.destroy()
    panel = Label(window, image = tkImage)
    panel.grid(column=1, row=1)
    window.update()

    window.after(0, updateImage)


BAUDRATE = 2000000
WIDTH = int(1280/2)
HEIGHT = int(960/2)

# Open tkinter window
window = Tk()  
window.title('Door Monitor')
window.geometry(f'{WIDTH}x{HEIGHT}')

# Create initial image
tkImage = ImageTk.PhotoImage(Image.open("Start.jpg"))
panel = Label(window, image = tkImage)
panel.grid(column=1, row=1)
window.update()

configure()
window.mainloop()

port.close()
sys.exit(0)