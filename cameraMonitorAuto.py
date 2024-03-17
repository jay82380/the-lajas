# Spresence imports
from serial import Serial
from io import BytesIO
from sys import exit
from tkinter import *
from PIL import ImageTk,Image
from time import sleep

def serialConfig():
    global port

    # Bind mouse click to start monitoring
    window.bind("<Button-1>", click)

    # Configure serial port
    port = Serial('/dev/tty.SLAB_USBtoUART', baudrate=BAUDRATE, timeout=3)
    port.flush()

def click(event):
    updateImage()

def updateImage():
    global panel

    # Message spresence to capture next image
    port.write('S'.encode())
    sleep(0.01)

    # Get the number of bytes for the image
    message = port.readline()
    message = str(message, "UTF-8")
    if(message == ''): print("TIMEOUT")

    # Read the image over serial
    bytes_read = port.read(int(message))
    if(len(bytes_read) < int(message)): print("TIMEOUT2")

    # Reconstruct the image from the received data
    image = Image.open(BytesIO(bytes_read))
    tkImage = ImageTk.PhotoImage(image)
  
    # Update image in window
    panel.destroy()
    panel = Label(window, image = tkImage)
    panel.grid(column=1, row=1)
    window.update()

    window.after(0, updateImage)

# Static spresence variables
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

serialConfig()
window.mainloop()

port.close()
exit(0)