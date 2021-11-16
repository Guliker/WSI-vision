"""
Used to send and receive from the customer portal script (CTO-script)
"""
import time
from paho.mqtt import client as mqtt_client

broker = 'broker.emqx.io'
port = 1883
# generate client ID with pub prefix randomly
# username = 'emqx'
# password = 'public'

def connect_mqtt(client_id = 'python-mqtt-default'):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    #client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, msg, topic="python/mqtt"):
    time.sleep(1)
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]

def subscribe(client, topic="python/mqtt"):
    def on_message(client, userdata, msg):
        print(msg.payload.decode())

    client.subscribe(topic)
    client.on_message = on_message

client = connect_mqtt()
client.loop_start()
publish(client,"hoi")
subscribe(client)
client.loop_forever()