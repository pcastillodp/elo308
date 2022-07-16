import paho.mqtt.client as mqttClient
import json
import time


connected = False
BROKER_ENDPOINT = "industrial.api.ubidots.com"
PORT = 1883
TOPIC  = "/v1.6/devices/"
MQTT_USERNAME = 'BBFF-yMNR3Otjl6H8tka4RmaEcCSZeXwt0J'
MQTT_PASSWORD = ''
DEVICE_LABEL = "raspberry/"
VARIABLE_LABEL = "prueba"

def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        print("Connected success")
        connected = True
    else:
        print(f"Connected fail with code {rc}")
        
def on_publish(client, userdata, result):
    print("Published!")
    
def connect(mqtt_client, mqtt_username, mqtt_password, broker_endpoint, port):
    global connected

    if not connected:
        mqtt_client.username_pw_set(mqtt_username, password=mqtt_password)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_publish = on_publish
        mqtt_client.connect(broker_endpoint, port=port)
        mqtt_client.loop_start()

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
    
def publish(mqtt_client, topic, payload):

    try:
        mqtt_client.publish(topic, payload)

    except Exception as e:
        print("[ERROR] Could not publish data, error: {}".format(e))


def main(mqtt_client):
    payload = json.dumps({"value": 20})
    topic = "{}{}{}".format(TOPIC, DEVICE_LABEL, VARIABLE_LABEL)

    

    if not connect(mqtt_client, MQTT_USERNAME,MQTT_PASSWORD, BROKER_ENDPOINT, PORT):
        return False
    print("tratando de publicar")
    publish(mqtt_client, topic, payload)

    return True


if __name__ == '__main__':
    mqtt_client = mqttClient.Client()
    while True:
        main(mqtt_client)
        time.sleep(10)
