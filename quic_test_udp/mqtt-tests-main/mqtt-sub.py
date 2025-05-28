
import random
import argparse
import sys
import ssl
from paho.mqtt import client as mqtt_client


broker = '127.0.0.1'
port = 1883
topic = "python/mqtt"
# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'

def set_transport(transport):
    if transport == 'tcp':
        return ('tcp', 1883, False)
    elif transport == 'tls':
        return ('tcp', 8883, True)
    elif transport == 'ws':
        return ('websockets', 8083, False)
    elif transport == 'wss':
        return ('websockets', 8084, True)

def connect_mqtt(broker, transport) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    transport, port, secure = set_transport(transport)
    client = mqtt_client.Client(client_id, transport=transport)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    if secure:
        client.tls_set(ca_certs='./ca-files/myCA.pem', certfile='ca-files/publisher/publisher.crt', cert_reqs=ssl.CERT_NONE, keyfile='ca-files/publisher/publisher.key', tls_version=ssl.PROTOCOL_TLSv1_2)
        client.tls_insecure_set(True)    
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message


def run(broker, transport):
    client = connect_mqtt(broker, transport)
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    # create argument parser
    parser = argparse.ArgumentParser(description='MQTT subscriber - Set the broker address, transport protocol, and port')
    parser.add_argument('-b', '--broker', help='Broker address', required=True)
    # parser.add_argument('-p', '--port', help='Broker port', required=True)
    parser.add_argument('-t', '--transport', help='Options are tcp, tls, ws, and wss', required=True)

    # parse arguments
    args = parser.parse_args()

    # check if broker is set
    if args.broker:
        # check if transport is given
        if args.transport in ['tcp', 'tls', 'ws', 'wss']:
            # run subscriber
            run(args.broker, args.transport)
               
        else:
            print('The transport %s is not supported' %args.transport)
    else:
        print('Broker address not given')
    
    # exit program
    sys.exit(0)