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
ip_monitoreo = "192.168.100.9" #ip servidor UDP
puerto_monitoreo = 1234
sucesor = ("192.168.100.9", 1234)  #ip y puerto del robot sucesor (prubea con servidor)
puerto_local = 1111
bufferSize = 1024

def udp_transm():   #Transmite informacion al robot sucesor
    global sucesor
    gl.t_actual = time.time() - gl.t_com_predecesor
    if (gl.t_actual >= 0.1):    #0.1 segundo
        cadena = "V/" + gl.parar + "/" + str(gl.Input_vel) + "/" + str(gl.vel_ref) + "/" + str(gl.curvatura)
        msg = str.encode(cadena)
        if(gl.flag_debug):
            print("voy a enviar al sucesor la cadena :" + cadena)
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPClientSocket.sendto(msg, sucesor)
        gl.t_com_predecesor = time.time()


