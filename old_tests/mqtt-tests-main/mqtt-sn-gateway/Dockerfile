FROM gcc:latest
RUN apt-get update && apt-get install -y cmake libgtest-dev libboost-test-dev && rm -rf /var/lib/apt/lists/* 
# COPY . /usr/src/
RUN mkdir -p /usr/src/
WORKDIR /usr/src/
RUN git clone https://github.com/eclipse/paho.mqtt-sn.embedded-c.git
WORKDIR /usr/src/paho.mqtt-sn.embedded-c/MQTTSNGateway/
RUN ./build.sh dtls
WORKDIR /usr/src/paho.mqtt-sn.embedded-c/MQTTSNGateway/bin
ENTRYPOINT ["./MQTT-SNGateway"]
