import picamera

camera = picamera.PiCamera()
camera.resolution = (1080, 720)
camera.start_recording('/home/pi/video.h264')
camera.wait_recording(30)
camera.stop_recording()
