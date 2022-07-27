# coding=utf-8
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
import os

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
    if(gl.flag_ubidots):
        t = threading.Thread(target = conexion.conectar_mqtt, args =() )    #hilo para levantar la conexion a Ubidots
        t.setDaemon(True)
        t.start()

    if(gl.flag_udp):
        ip_local = os.popen('hostname -I').read().strip()
        print(configuracion.lider[0])

        if(ip_local == configuracion.lider[0]): gl.flag_robot = "L"
        elif(ip_local == configuracion.seguidor1[0]): gl.flag_robot = "S1"
        elif(ip_local == configuracion.seguidor2[0]): gl.flag_robot = "S2"
        elif(ip_local == configuracion.seguidor3[0]): gl.flag_robot = "S3"
        elif(ip_local == configuracion.seguidor4[0]): gl.flag_robot = "S4"
        else: gl.flag_robot = "L"

        if(gl.flag_debug or gl.flag_debug_udp):
            print("soy el agente : " + gl.flag_robot)

        t_udp = threading.Thread(target =  conexion.setup_udp, args =() )   #abre servidor UDP para recibir mensajes
        t_udp.setDaemon(True)
        t_udp.start()
    
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
            if(gl.flag_debug):
                print("pasando a inicio")
        elif(estado==controlLoop and (gl.parar=="no")):
            estado_siguiente=controlLoop
        elif(estado==controlLoop and (gl.parar=="si")):
            estado_siguiente=inicio
        else:
            estado_siguiente=inicio
        estado=estado_siguiente
    
if __name__ == "__main__":
    main()
