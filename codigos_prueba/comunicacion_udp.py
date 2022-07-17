# coding=utf-8
import random
import time
import socket
import threading

"""
    Logica de comunicacion simulada:
    La comunicacion empieza por el monitor enviando un "L/" al lider para solicitar datos
    El lider al recibir, envia datos al monitor y al seguidor1 de la forma "V/" y parar, Input_vel, vel_ref, curvatura
    Seguidor1 al recibir envia sus datos al seguidor2

    seguidor2 -> seguidor1 -> lider -> monitor
"""

flag_robot = "S1" #M:monitor ; L:lider ; S1:seguidor 1 ; S2:seguidor 2

#UDP
bufferSize = 1024
socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket_udp.connect(("8.8.8.8", 80))
data = bytearray()

monitor = ("192.168.100.9", 1234)   #ip y puerto pc windows
lider = ("192.168.100.20", 1111)    #ip y puerto de la raspberry
seguidor1 = ("192.168.100.22", 1111)   #ip y puerto del robot sucesor 
seguidor2 = ("192.168.100.23", 1111)   #ip y puerto del robot sucesor 

def main(args=None):
    global socket_udp, lider
    
    ip_local= socket_udp.getsockname()[0]
    if (ip_local == "192.168.100.9"): flag_robot = "M"
    elif(ip_local == "192.168.100.20"): flag_robot = "L"
    elif(ip_local == "192.168.100.22"): flag_robot = "S1"
    elif(ip_local == "192.168.100.23"): flag_robot = "S2"

    print(socket_udp.getsockname()[0])

    if(flag_robot=="M"):
        print("soy el monitor")
        print("escribe L/ para solicitarle datos al lider")
        mensaje = input("escribe el mensaje a enviar: ")
        if (mensaje == "L/"):
            solicitar(lider)
            t_udp = threading.Thread(target =  self.recibir, args =(lider) ) 
            t_udp.setDaemon(True)
            t_udp.start()

    elif(flag_robot == "L"):
        print("soy el lider")
        print("estare atento al monitor por si solicitan datos")
        t_udp = threading.Thread(target=recibir,args =(lider)) 
        t_udp.setDaemon(True)
        t_udp.start()



def enviar (sujeto):
    print("enviar")
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
    print("solicitar")
    global socket_udp
    cadena = "L/"
    msg = str.encode(cadena)
    print("estoy solicitando datos con la cadena: " + cadena + "al robot " + sujeto)
    socket_udp.sendto(msg, sujeto)


def recibir(sujeto):
    print("recibir")
    global socket_udp
    print('abriendo servidor udp en {} port {}'.format(*sujeto))
    socket_udp.bind(sujeto)
    while True:
        print('\nesperando a recibir mensajes')
        data, address = socket_udp.recvfrom(4096)

        print('received {} bytes from {}'.format(len(data), address))
        print(data)

if __name__ == "__main__": 
  main()
  
