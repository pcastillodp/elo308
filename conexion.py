import threading
import paho.mqtt.client as mqttClient
import json
import time
import gl

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
        print("Connected success")
        print("Suscrito a: " + TOPIC_SUSCRITO)
        connected = True
        client.subscribe(TOPIC_SUSCRITO)
    else:
        print(f"Connected fail with code {rc}")
        
def on_publish(client, userdata, result):
    print("Published!")
  
# The callback for when a message is received from the server.
def on_message(client, userdata, msg):
    global distancia_kp, distancia_ki, distancia_kd
    global theta_kp, theta_ki, theta_kd
    global velocidad_kp, velocidad_ki, velocidad_kd
    print("sisub: msg received with topic: {} and payload: {}".format(msg.topic, str(msg.payload)))
    variable = msg.topic.split('/')[4]  
    valor = msg.payload.decode("utf-8") 
    if (variable == "distancia_kp"):
        gl.Kp_distancia = valor
        print("hola")
    
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
            print(connected)
            print("Attempting to connect...")
            time.sleep(1)
            attempts += 1

    if not connected:
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
    print("topico publicado: " + str(topic))

