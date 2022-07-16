import smbusr
from time import sleep
import RPi.GPIO as GPIO
import Adafruit_ADS1x15

GPIO.setmode(GPIO.BOARD)
adc = Adafruit_ADS1x15.ADS1115()

#Definiciones
S0=31
S1=33
S2=35
S3=37
channel = 1
address= 0x48
GAIN = 2/3

i2c = smbus.SMBus(channel)
GPIO.setup(S0, GPIO.OUT)
GPIO.setup(S1, GPIO.OUT)
GPIO.setup(S2, GPIO.OUT)
GPIO.setup(S3, GPIO.OUT)

def main(args=None):
	GPIO.output(S0, GPIO.LOW)
	GPIO.output(S1, GPIO.HIGH)
	GPIO.output(S2, GPIO.HIGH)
	GPIO.output(S3, GPIO.LOW)
	
	while True:
		values = [0]*4
		
		for i in range(4):
			values[i] = adc.read_adc(i, gain=GAIN)
		print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
		
		sleep(0.5)
		

if __name__ == "__main__":
    main()





