#FUNCIONANDO OK
from time import sleep
import smbus
import RPi.GPIO as GPIO
import Adafruit_ADS1x15

GPIO.setmode(GPIO.BOARD)
adc = Adafruit_ADS1x15.ADS1115()

#Definiciones
SIGNAL=29
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
	values = [0]*16
	maximo = [0]*16
	minimo = [32000]*16
	print("calibrando!")
	for i in range (20):
		for s in range(16):
			GPIO.output(S0, s&0x01) # 0001
			GPIO.output(S1, s&0x02) # 0010
			GPIO.output(S2, s&0x04) # 0100
			GPIO.output(S3, s&0x08) # 1000
			valor = adc.read_adc(0, gain=GAIN)
			maximo[s] = valor if (valor > maximo[s]) else (maximo[s])
			minimo[s] = valor if (valor < minimo[s]) else (minimo[s])
			sleep(0.01)
	print(maximo)
	print(minimo)
	while True:
		for s in range(16):
			GPIO.output(S0, s&0x01) # 0001
			GPIO.output(S1, s&0x02) # 0010
			GPIO.output(S2, s&0x04) # 0100
			GPIO.output(S3, s&0x08) # 1000
			values[s] = adc.read_adc(0, gain=GAIN)
			rango = maximo[s] - minimo[0]
			th_h = maximo[s] - rango*0.5
			th_l = minimo[s] + rango*0.5
			values[s] = 0 if (values[s] >= th_h) else 1
			sleep(0.01)
		print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} | {4:>6} | {5:>6} | {6:>6} | {7:>6} |'.format(*values))
		print("|                                                                       |")
		print("|                                                                       |")
		print('| {8:>6} | {9:>6} | {10:>6} | {11:>6} | {12:>6} | {13:>6} | {14:>6} | {15:>6} |'.format(*values))
		print("-------------------------------------------------------------------------")
		sleep(0.5)

if __name__ == "__main__":
    main()
