# coding=utf-8
#  Función de motor  
from time import sleep
import RPi.GPIO as GPIO
import configuracion
GPIO.setmode(GPIO.BOARD)
from numpy import interp

global pwma
global pwmb
pwma = GPIO.PWM(configuracion.PWMA, configuracion.freqPWM)	#se crea la instancia PWM con frecuencia de 500 Hz
pwmb = GPIO.PWM(configuracion.PWMB, configuracion.freqPWM)

pwma.start(0)	#se inicia el PWM con dutycicle de 0
pwmb.start(0)



def motor (velocidadMotorIzq, velocidadMotorDer):

	#Función de motor motor(M1, M2).
	#Mueve los motores con velocidad M1 y M2 con un valor entero entre 0 y 1024
	#En caso de introducir un número negativo, el motor se mueve en sentido inverso.
	
	if (velocidadMotorDer >= configuracion.resolucionPWM):
		velocidadMotorDer=configuracion.resolucionPWM
	elif (velocidadMotorDer <= - configuracion.resolucionPWM):
		velocidadMotorDer=-configuracion.resolucionPWM
	if(velocidadMotorIzq >= configuracion.resolucionPWM):
		velocidadMotorIzq=configuracion.resolucionPWM
	elif (velocidadMotorIzq <= - configuracion.resolucionPWM):
		velocidadMotorIzq=-configuracion.resolucionPWM
		
	
	if(velocidadMotorDer>0):
		runMotor(0,velocidadMotorDer,0)
	elif (velocidadMotorDer<0):
		runMotor(0,-velocidadMotorDer,1)
	else:
		runMotor(0,0,0)
	
	if(velocidadMotorIzq>0):
		runMotor(1,velocidadMotorIzq,0)
	elif (velocidadMotorIzq<0):
		runMotor(1,-velocidadMotorIzq,1)
	
	else:
		runMotor(1,0,0)
		
		
		
def runMotor(motor, vel, direccion): #motor 0: derecha
	in1 = GPIO.LOW
	in2 = GPIO.HIGH
	
	if(vel == 0):
		GPIO.output(configuracion.AIN1, GPIO.LOW)
		GPIO.output(configuracion.AIN2, GPIO.LOW)
		GPIO.output(configuracion.BIN1, GPIO.LOW)
		GPIO.output(configuracion.BIN2, GPIO.LOW)
		pwma.ChangeDutyCycle(0)
		pwmb.ChangeDutyCycle(0)
		
	else:
		if(direccion == 1):	#direccion inversa
			in1 = GPIO.HIGH
			in2 = GPIO.LOW

		if (motor == 0):	#motor derecho
			GPIO.output(configuracion.AIN1, in1)
			GPIO.output(configuracion.AIN2, in2)
			vel = vel * (100/configuracion.resolucionPWM)		#se realiza el mapeo de 0-1024 (resolucionPWM) a 0-100
			pwma.ChangeDutyCycle(vel)

		elif (motor == 1):	#motor izquierdo
			GPIO.output(configuracion.BIN1, in2)
			GPIO.output(configuracion.BIN2, in1)
			vel = vel * (100/configuracion.resolucionPWM)		#se realiza el mapeo de 0-1024 (resolucionPWM) a 0-100
			pwmb.ChangeDutyCycle(vel)
