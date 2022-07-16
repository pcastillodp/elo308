#FUNCIONANDO OK
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

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
    tiempoPrueba = 1
    velocidad = 20
    
    print("adelante")
    adelante(velocidad)
    sleep(tiempoPrueba)
    
    motorStop()    
    sleep(.25)
     
    print("atras")
    atras(velocidad)
    sleep(tiempoPrueba)
    motorStop()
    
    motorStop()    
    sleep(.25)
    
    print("derecha")
    giroDerecha(velocidad)
    sleep(tiempoPrueba)
    motorStop()
    
    motorStop()    
    sleep(.25)
    
    print("izquierda")
    giroIzquierda(velocidad)
    sleep(tiempoPrueba)
    motorStop()
    
    print("test de encoder")
    
    for i in range (20):
        print(str(GPIO.input(encoderD)) + " || " + str(GPIO.input(encoderL)))
        sleep(0.5)
if __name__ == "__main__":
    main()
