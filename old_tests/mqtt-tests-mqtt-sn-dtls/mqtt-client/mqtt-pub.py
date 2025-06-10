import random
import time
import argparse
from paho.mqtt import client as mqtt_client
import ssl
import sys

broker = '127.0.0.1'
port = 1883
topic = "python/mqtt"
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
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



def publish(client, n_messages=5, msg_size=1, msg_interval=1):
    msg_count = 1
    while True:
        msg = msg_size * "0"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
        if msg_count > n_messages:
            break
        time.sleep(msg_interval)


def run(broker, transport, n_messages=5, msg_size=1, msg_interval=1):
    client = connect_mqtt(broker, transport)
    client.loop_start()
    publish(client, n_messages, msg_size, msg_interval)
    client.loop_stop()


if __name__ == '__main__':
    # create argument parser
    parser = argparse.ArgumentParser(description='MQTT subscriber - Set the broker address, transport protocol, and port')
    parser.add_argument('-b', '--broker', help='Broker address', required=True)
    # parser.add_argument('-p', '--port', help='Broker port', required=True)
    parser.add_argument('-t', '--transport', help='Options are tcp, tls, ws, and wss', required=True)
    parser.add_argument('-n', '--n_messages', help='The number of messages published', required=False)
    parser.add_argument('-s', '--msg_size', help='The message size in bytes', required=False)
    parser.add_argument('-i', '--msg_interval', help='The interval between messages in seconds', required=False)

    # parse arguments
    args = parser.parse_args()
    msg_size = args.msg_size if args.msg_size else 1
    n_messages = args.n_messages if args.n_messages else 5
    msg_interval = args.msg_interval if args.msg_interval else 1

    time.sleep(1)
    # check if broker is set
    if args.broker:
        # check if transport is given
        if args.transport in ['tcp', 'tls', 'ws', 'wss']:
            # run subscriber
            run(args.broker, args.transport, int(n_messages), int(msg_size), float(msg_interval))
               
        else:
            print('The transport %s is not supported' %args.transport)
    else:
        print('Broker address not given')
    
    time.sleep(1)
    # exit program
    sys.exit(0)