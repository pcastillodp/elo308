import picamera

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.start_recording('/home/pi/video.h264')
camera.wait_recording(30)
camera.stop_recording()
