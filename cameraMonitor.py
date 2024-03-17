import serial
import io
from PIL import Image
from time import sleep

BAUDRATE = 2000000

# Configure serial port
port = serial.Serial('/dev/tty.SLAB_USBtoUART', baudrate=BAUDRATE)
port.flush()

while True:
    input("Press enter to get image: ")
    port.write('S'.encode())
    sleep(0.001)

    # Get the number of bytes for the image
    print("Reading the image...")
    message = port.readline()
    message = message.decode()
    message = ''.join(filter(lambda x: x != '\x00', message))
    print(message)

    # Read the image over serial
    bytes_read = port.read(int(message))

    # Reconstruct the image from the received data
    print("Image received")
    image = Image.open(io.BytesIO(bytes_read))
    image.show()

port.close()