import threading
import paho.mqtt.client as mqttClient
import socket
import json
import time
import gl



"""
    Implementacion de MQTT (Ubidots)
"""
#configuracion para ubidots
global mqtt_client
connected = False
BROKER_ENDPOINT = "industrial.api.ubidots.com"
PORT = 1883
TOPIC  = "/v1.6/devices/"
MQTT_USERNAME = 'BBFF-yMNR3Otjl6H8tka4RmaEcCSZeXwt0J'
MQTT_PASSWORD = ''
DEVICE_LABEL = "raspberry/"
VARIABLE_LABEL = "prueba"
TOPIC_SUSCRITO = "/v1.6/devices/controlador/+/lv"

def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        if(gl.flag_debug):
            print("Connected success")
            print("Suscrito a: " + TOPIC_SUSCRITO)
        connected = True
        client.subscribe(TOPIC_SUSCRITO)
    else:
        if(gl.flag_debug):
            print(f"Connected fail with code {rc}")
        
def on_publish(client, userdata, result):
    if(gl.flag_debug):
        print("Published!")
  
# The callback for when a message is received from the server.
def on_message(client, userdata, msg):
    global distancia_kp, distancia_ki, distancia_kd
    global theta_kp, theta_ki, theta_kd
    global velocidad_kp, velocidad_ki, velocidad_kd
    if(gl.flag_debug):
        print("sisub: msg received with topic: {} and payload: {}".format(msg.topic, str(msg.payload)))
    variable = msg.topic.split('/')[4]  
    valor = msg.payload.decode("utf-8") 
    if (variable == "distancia_kp"):
        gl.Kp_distancia = valor
    
def connect(mqtt_client, mqtt_username, mqtt_password, broker_endpoint, port):
    global connected

    if not connected:
        mqtt_client.username_pw_set(mqtt_username, password=mqtt_password)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_publish = on_publish
        mqtt_client.on_message = on_message
        mqtt_client.connect(broker_endpoint, port=port)
        mqtt_client.loop_forever()

        attempts = 0

        while not connected and attempts < 5:  # Wait for connection
            if(gl.flag_debug):
                print(connected)
                print("Attempting to connect...")
            time.sleep(1)
            attempts += 1

    if not connected:
        if(gl.flag_debug):
            print("[ERROR] Could not connect to broker")
        return False

    return True

def conectar_mqtt():
	global mqtt_client
	mqtt_client = mqttClient.Client()
	connect(mqtt_client, MQTT_USERNAME,MQTT_PASSWORD, BROKER_ENDPOINT, PORT)
	
def publicar(variable, valor):
    global mqtt_client
    payload = json.dumps({"value": valor})
    topic = "{}{}{}".format(TOPIC, DEVICE_LABEL, variable)
    mqtt_client.publish(topic, payload)
    if(gl.flag_debug):
        print("topico publicado: " + str(topic))


"""
    Implementacion de UDP
"""

#configuracion para UDP
monitor = ("192.168.100.9", 1234)   #ip y puerto pc windows
local = ("192.168.100.18", 1111)   #ip y puerto de la raspberry
sucesor = ("192.168.100.9", 1234)  #ip y puerto del robot sucesor (prubea con servidor)
bufferSize = 1024
socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
global data

def udp_transm():   #Transmite informacion al robot sucesor
    global socket_udp, sucesor
    gl.t_actual = time.time() - gl.t_com_predecesor
    if (gl.t_actual >= 0.1):    #0.1 segundo
        cadena = "V/" + gl.parar + "/" + str(gl.Input_vel) + "/" + str(gl.vel_ref) + "/" + str(gl.curvatura)
        msg = str.encode(cadena)
        if(gl.flag_debug):
            print("voy a enviar al sucesor la cadena :" + cadena)
        #socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        socket_udp.sendto(msg, sucesor)
        gl.t_com_predecesor = time.time()

def setup_udp():
    global socket_udp, local, data
    if(gl.flag_debug):
        print('abriendo servidor udp en {} port {}'.format(*local))
    socket_udp.bind(local)
    while True:
        if(gl.flag_debug):
            print('\nesperando a recibir mensajes')
        data, address = socket_udp.recvfrom(4096)

        if(gl.flag_debug):
            print('received {} bytes from {}'.format(len(data), address))
            print(data)

        #if data:
        #    sent = socket_udp.sendto(data, address)
        #    if(True):
        #        print('sent {} bytes back to {}'.format(sent, address))

def udp_recep():    #recibe datos del predecesor 
    global data
    paquete_entrante = data
    len_data = len(data)
    if (len_data > 0):
        paquete_entrante[len_data] = 0
    if(paquete_entrante[0] == "L"):
        if(gl.flag_debug):
            print("recibi un L, monitor esta pidiendo datos")
        lectura_estado(len_data)
    #elif (paquete_entrante[0]== "E"):   #queda deshabilitado porque se hace a traves de ubidots
    #    if(gl.flag_debug):
    #        print("recibi un E de escritura")
    #    cadena = configuracion_remota(len_data)
    #    msg = str.encode(cadena)
    elif(paquete_entrante[0] == "V"):
        if(gl.flag_debug):
            print("recibi un V, envio de datos del predecesor")   
        estado_predecesor(len_data)

def lectura_estado(len_data):
    global data, socket_udp, monitor
    mensaje = data
    if (mensaje == "/estado_predecesor"):
        cadena = "V/" + gl.parar + "/" + str(gl.Input_vel) + "/" + str(gl.vel_ref) + "/" + str(gl.curvatura_predecesor)
    else:
        cadena = "incorrecto"
    for i in range (3):
        msg = str.encode(cadena)
        if(gl.flag_debug):
            print("voy a enviar al monitor la cadena :" + cadena)
        socket_udp.sendto(msg, monitor)


def estado_predecesor(len_data):
    global data
    mensaje = data
    print("funcion estado predecesor")
    print(mensaje)




