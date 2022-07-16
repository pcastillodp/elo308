from time import sleep
import RPi.GPIO as GPIO
import smbus
import Adafruit_ADS1x15

GPIO.setmode(GPIO.BOARD)
adc = Adafruit_ADS1x15.ADS1115()

#Definiciones
pwmFreq = 100
PWMA = 12
AIN2 = 18
AIN1 = 16
BIN1 = 15
BIN2 = 13
PWMB = 11
radioRueda = 2
encoderD=19
encoderL=23
SIGNAL=29
S0=31
S1=33
S2=35
S3=37
channel = 1
address= 0x48
GAIN = 2/3

#PID
Kp_theta = 0.002
Kd_theta = 0.004

i2c = smbus.SMBus(channel)

GPIO.setup(S0, GPIO.OUT)
GPIO.setup(S1, GPIO.OUT)
GPIO.setup(S2, GPIO.OUT)
GPIO.setup(S3, GPIO.OUT)
GPIO.setup(PWMA, GPIO.OUT) 
GPIO.setup(AIN2, GPIO.OUT) 
GPIO.setup(AIN1, GPIO.OUT) 
GPIO.setup(BIN1, GPIO.OUT) 
GPIO.setup(BIN2, GPIO.OUT) 
GPIO.setup(PWMB, GPIO.OUT) 
GPIO.setup(encoderD, GPIO.IN)
GPIO.setup(encoderL, GPIO.IN)

pwma = GPIO.PWM(PWMA, pwmFreq)
pwmb = GPIO.PWM(PWMB, pwmFreq)
pwma.start(100)
pwmb.start(100)

def adelante(vel):
    runMotor(0, vel, 0)
    runMotor(1, vel, 0)

def atras(vel):
    runMotor(0, vel, 1)
    runMotor(1, vel, 1)
    
def giroDerecha(vel):
    runMotor(0, vel, 1)
    runMotor(1, vel, 0)
    
def giroIzquierda(vel):
    runMotor(0, vel, 0)
    runMotor(1, vel, 1)

def runMotor(motor, vel, direccion):
    in1 = GPIO.LOW
    in2 = GPIO.HIGH

    if(direccion == 1):
        in1 = GPIO.HIGH
        in2 = GPIO.LOW

    if (motor == 0):
        GPIO.output(AIN1, in1)
        GPIO.output(AIN2, in2)
        pwma.ChangeDutyCycle(vel)

    elif (motor == 1):
        GPIO.output(BIN1, in2)
        GPIO.output(BIN2, in1)
        pwmb.ChangeDutyCycle(vel)

def motorStop():
    pwma.ChangeDutyCycle(0)
    pwmb.ChangeDutyCycle(0)
    

def main(args=None):
	velocidadMaxima = 70
	velocidad = velocidadMaxima/2
	values = [0]*16
	ponderacion = [0]*16 #se consideran solo los sensores de delante
	
	motorStop()
	
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
	
	print("andemos!")
	
	while True:
		posicion = 0
		error = 0
		errorPasado = 0
		deltaVelocidad = 0
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
			ponderacion[s] = values[s] * 1000 * (s+1)
			sleep(0.01)
			
		activos = 0	
		for s in range(8):
			if(ponderacion[s] > 0):
				posicion = posicion + ponderacion[s]
				activos = activos +1
		
		posicion = (posicion / activos) if (activos > 0) else 0
		#print(str(ponderacion[0]) + " " + str(ponderacion[1]) + " " + str(ponderacion[2]) + " " + str(ponderacion[3]) + " " + str(ponderacion[4]) + " " + str(ponderacion[5]) + " " + str(ponderacion[6]) + " " + str(ponderacion[7]))
			
		if (posicion > 0):
			error = posicion - 4500
			velocidadMotor = Kp_theta*error + (error - errorPasado)*Kd_theta
			errorPasado = error
			
			velocidadDerecho = velocidad - velocidadMotor if ((velocidad - velocidadMotor)<velocidadMaxima) else velocidadMaxima
			velocidadIzquierdo = velocidad + velocidadMotor if ((velocidad + velocidadMotor)<velocidadMaxima) else velocidadMaxima
			
			velocidadDerecho = velocidadDerecho if (velocidadDerecho > 0) else 0
			velocidadIzquierdo = velocidadIzquierdo if (velocidadIzquierdo > 0) else 0
			
			print("posicion: " + str(posicion) + " error: " + str(error))
			
			print("Vel DER: " + str(velocidadDerecho) + " Vel IZQ: " + str(velocidadIzquierdo))
			
			
			runMotor(0, velocidadDerecho, 0)
			runMotor(1, velocidadIzquierdo, 0)
			
		else:
			print("posicion 0")
			motorStop()
			
		print("......")
		sleep(0.01)
		

if __name__ == "__main__":
    main()
