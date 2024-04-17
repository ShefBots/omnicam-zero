from picamera2 import Picamera2, Preview
import os

# Create a place to store images
os.makedirs('configuration-images', exist_ok=True)

picam = Picamera2()
config = picam.create_preview_configuration()
picam.configure(config)

picam.capture_file("test-image.jpg")

picam.close()
