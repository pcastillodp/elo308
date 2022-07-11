from time import sleep
#import RPi.GPIO as GPIO
import actuadores
import configuracion
import sensores
import estados
import gl
import conexion
import logging	#para crear el archivo que almacena los datos 
import threading    #hilos

global mqtt_client

logging.basicConfig(filename="log.txt", level=logging.INFO,
                    format="%(asctime)s %(message)s")


#maquina de estados
inicio = 0
calibracion = 1
controlLoop = 2
estado = 0
estado_siguiente = 0


def main(args=None):
    
    t = threading.Thread(target = conexion.conectar_mqtt, args =() )    #hilo para levantar la conexion a Ubidots
    t.setDaemon(True)
    t.start()
    
    sensores.configuracionSensorD()
    global estado, inicio, calibracion, controlLoop, calibrar, parar
    
    while True:
        if (estado == inicio):
            estados.ciclo_de_inicio()
        elif (estado == calibracion):
            estados.ciclo_de_calibracion()
        elif(estado == controlLoop):
            estados.ciclo_de_control()
        else:
            sensores.ciclo_de_inicio()

        if(estado == inicio and gl.calibrar):
            estado_siguiente=calibracion
            #print("pasando a calibracion")
            input()
        elif(estado==inicio and (gl.parar=='si')):
            estado_siguiente=inicio
        elif(estado==inicio and (gl.parar=='no')):
            estado_siguiente=controlLoop
        elif(estado==calibracion):
            estado_siguiente=inicio
            print("pasando a inicio")
        elif(estado==controlLoop and (gl.parar=="no")):
            estado_siguiente=controlLoop
        elif(estado==controlLoop and (gl.parar=="si")):
            estado_siguiente=inicio
        else:
            estado_siguiente=inicio
        estado=estado_siguiente
    
    #sensores.calibrarSensor()
    
    #for s in range (200):
    #    print(sensores.distancia())
    #    sleep(0.1)
    
    #sensores.velocidades()
    
    #print("adelante")
    #actuadores.motor(30,30)
    #sleep(1)
    
    #print("atras")
    #actuadores.motor(-30,-30)
    #sleep(1)
        
    #print("parar")
    #actuadores.motor(0,0)
    #sleep(.25)

if __name__ == "__main__":
    main()
