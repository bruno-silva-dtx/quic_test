# MQTT-SN Gateway Repository

This repository contains the code for an MQTT-SN Gateway using the Paho MQTT-SN library. Follow the instructions below to set up and run the gateway.

## Pre requisites

Before you begin, ensure you have the following dependencies installed:

- Docker
- Python 3.8
- CMake
- Paho code from: https://github.com/eclipse/paho.mqtt-sn.embedded-c.git
- MQTT-SN python code from: http://www.steves-internet-guide.com/python-mqttsn-client/

## Setup

1. **Start Docker Containers**: Run the following command to start the required Docker containers in the background:

   ```bash
   docker-compose up -d
   ```

2. **Build MQTT-SN Gateway**: Navigate to the `MQTTSNGateway` directory in the Paho MQTT-SN library and run the build script:

   ```bash
   git clone https://github.com/eclipse/paho.mqtt-sn.embedded-c.git
   cd paho.mqtt-sn.embedded-c/MQTTSNGateway
   ./build.sh dtls
   ```

   Use `dtls` if you want to build a DTLS (Datagram Transport Layer Security) gateway; there are other options available as well. This will start the MQTT-SN Gateway and allow you to subscribe to the specified topic.

## Configuration

After building the MQTT-SN Gateway, configure it as follows:

- In the `gateway.conf` file:
  - Change the broker name (`127.0.0.1`) to the address of your MQTT broker.
  - Change the gateway port number (`1885`) to your desired port.
  - Update the directory for certificates after creating your certificates, to ensure secure communication (don't forget to add it in .gitignore). 

## Connecting Gateway to Broker

To connect the MQTT-SN Gateway to the MQTT broker, follow these steps:

1. Navigate to the `bin` directory within the MQTT-SN Gateway folder:

   ```bash
   cd bin
   ```

2. Run the MQTT-SN Gateway executable:

   ```bash
   ./MQTT-SNGateway
   ```

   This will start the gateway and connect it to your MQTT broker using the settings defined in the `gateway.conf` file.

## Usage

3. **Run MQTT-SN Client**: You can use the Python MQTT-SN Client example provided in the `mqtt-sn-client` directory. Navigate to the `mqtt-sn-client` directory and run the following command to subscribe to the topic:

   ```bash
   cd mqtt-sn-client
   python3 pub-sub-sn.py

   ```

   This will allow you to subscribe to the specified topic.

# MQTT Repository
These are the instructions to run MQTT to test the broker without the protection layer. 
## Setup

1. **Start Docker Containers**: Run the following command to start the required Docker containers in the background:

   ```bash
   docker-compose up -d
   ```

2. **Run MQTT Client**:

In one terminal, you subscribe to the broker:
```bash
   mqtt-sub.py -b BROKER -t TRANSPORT
ex: python mqtt-sub.py -b 127.0.0.1 -t ws
   ```
In another terminal, you publish to the broker:
```bash 
   mqtt-pub.py -b BROKER -t TRANSPORT [-n N_MESSAGES] [-s MSG_SIZE] [-i MSG_INTERVAL]
ex: python mqtt-pub.py -b 127.0.0.1 -t ws
```







