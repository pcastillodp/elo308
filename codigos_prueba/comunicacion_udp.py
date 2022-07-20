# coding=utf-8
import random
import time
import socket
import threading
import os

"""
    Logica de comunicacion simulada:
    La comunicacion empieza por el monitor enviando un "L/" al lider para solicitar datos
    El lider al recibir, envia datos al monitor y al seguidor1 de la forma "V/" y parar, Input_vel, vel_ref, curvatura
    Seguidor1 al recibir envia sus datos al seguidor2

    seguidor2 -> seguidor1 -> lider -> monitor
"""

flag_robot = "S1" #M:monitor ; L:lider ; S1:seguidor 1 ; S2:seguidor 2 ; S3:seguidor3

#UDP
bufferSize = 1024
socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
#socket_udp.connect(("8.8.8.8", 80))
data = bytearray()

monitor = ("192.168.100.9", 1234)   #ip y puerto pc windows
lider = ("192.168.100.18", 1111)    #ip y puerto de la raspberry
seguidor1 = ("192.168.100.20", 1111)   #ip y puerto del robot sucesor 
seguidor2 = ("192.168.100.22", 1111)   #ip y puerto del robot sucesor 
seguidor3 = ("192.168.100.23", 1111)  


def main(args=None):
    global socket_udp, lider, flag_robot
    
    ip_local = os.popen('hostname -I').read().strip()

    if (ip_local == "192.168.100.9"): flag_robot = "M"
    elif(ip_local == "192.168.100.18"): flag_robot = "L"
    elif(ip_local == "192.168.100.20"): flag_robot = "S1"
    elif(ip_local == "192.168.100.22"): flag_robot = "S2"
    elif(ip_local == "192.168.100.23"): flag_robot = "S3"
    else: flag_robot = "M"

    if(flag_robot=="M"):
        print("soy el monitor")
        print("escribe L/ para solicitarle datos al lider")
        mensaje = input("escribe: ")
        if (mensaje == "L/"):
            print("abriendo puerto de escucha")
            recibir(monitor)
            
    elif(flag_robot == "L"):
        print("soy el lider")
        print("estare atento por si solicitan datos")
        t_udp = threading.Thread(target=recibir, args = (lider,)) 
        t_udp.setDaemon(True)
        t_udp.start()
        
    elif(flag_robot=="S1"):
        print("soy el seguidor1")
        print("estare atento por si me llegan datos")
        t_udp = threading.Thread(target=recibir, args = (seguidor1,)) 
        t_udp.setDaemon(True)
        t_udp.start()
    
    elif(flag_robot=="S2"):
        print("soy el seguidor2")
        print("estare atento por si me llegan datos")
        t_udp = threading.Thread(target=recibir, args = (seguidor2,)) 
        t_udp.setDaemon(True)
        t_udp.start()
    
    elif(flag_robot=="S3"):
        print("soy el seguidor3")
        print("estare atento por si me llegan datos")
        t_udp = threading.Thread(target=recibir, args = (seguidor3,)) 
        t_udp.setDaemon(True)
        t_udp.start()
        
        
    while(True):
        time.sleep(1000)
        

def enviar (sujeto):
    print("funcion enviar")
    global socket_udp
    parar = "si"
    Input_vel = random.randint(0,22)
    vel_ref = random.randint(0,22)
    curvatura = random.randint(0,22)

    cadena = "V/" + parar + "/" + str(Input_vel) + "/" + str(vel_ref) + "/" + str(curvatura)
    msg = str.encode(cadena)
    print("voy a enviar la cadena: " + cadena + "al robot" + sujeto)
    socket_udp.sendto(msg, sujeto)

    
def solicitar(sujeto):
    print("funcion solicitar")
    global socket_udp
    cadena = "L/"
    msg = str.encode(cadena)
    print("estoy solicitando datos con la cadena: " + cadena + " al robot "  .format(*sujeto))
    socket_udp.sendto(msg, sujeto)


def recibir(sujeto):
    global socket_udp, data, flag_robot, monitor, lider, seguidor1, seguidor2, seguidor3
    print("funcion recibir")
    print('abriendo servidor udp en {} port {}'.format(*sujeto))
    socket_udp.bind(sujeto)
    if (flag_robot == "M"):
        print("enviando mensaje L")
        solicitar(lider)
    while True:
        print('\nesperando a recibir mensajes')
        data, address = socket_udp.recvfrom(4096)
        print('received {} bytes from {}'.format(len(data), address))
        paquete_entrante = data.decode('UTF-8')
        len_data = len(data)
        if (len_data > 0):
            print("el mensaje fue " + paquete_entrante)
            if(paquete_entrante[0] == "L"):
                print("recibi un L, estan pidiendo datos")
                if (flag_robot == "L"):
                    print("enviando datos al monitor")
                    enviar(monitor)
                    print("enviando datos al seguidor1")
                    enviar(seguidor1)
            else:
                if(flag_robot== "M"):
                    print("recibi datos del lider")
                elif(flag_robot == "S1"):
                    print("recibi datos del lider, voy a enviar los mios a S2")
                    enviar(seguidor2)
                elif(flag_robot == "S2"):
                    print("recibi datos del S1, voy a enviar los mios a S3")
                    enviar(seguidor3)
                elif(flag_robot=="S3"):
                    print("recibi datos del S2")
                

        
        

            

if __name__ == "__main__": 
  main()
  
