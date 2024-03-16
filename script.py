import serial

# Configure serial port
ser = serial.Serial('/dev/ttyCOM4', 115200)  # Update port name if needed

# Read image data from serial and save it to a file
with open('image.jpg', 'wb') as f:
    while True:
        data = ser.read(1024)  # Read 1024 bytes at a time
        if not data:
            break
        f.write(data)

print("Image received and saved as 'image.jpg'")
