from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.rotation = 180

camera.start_preview()
camera.start_recording('/home/pi/video4.h264')
sleep(30)
camera.stop_recording()
camera.stop_preview()
camera.stop_preview()
