#!/bin/bash

# Verificando se o número de argumentos está correto
if [ "$#" -ne 5 ]; then
    echo "Uso: $0 <qos> <topic> <size_of_packets> <number_of_packets> <msg_interval>"
    exit 1
fi

# Atribuindo os argumentos a variáveis
QOS="$1"
TOPIC="$2"
SIZE_OF_PACKETS="$3"
NUMBER_OF_PACKETS="$4"
MSG_INTERVAL="$5"

# Publica mensagens em um broker MQTT usando o quic_client
/root/quic_mqtt/build/quic_client pub 'mqtt-tcp://emqx:14567' "$QOS" "$TOPIC" "$SIZE_OF_PACKETS" "$NUMBER_OF_PACKETS" "$MSG_INTERVAL"

# /root/quic_mqtt/build/quic_client pub 'mqtt-tcp://emqx:14567' 0 topic 100 5 50
#   %s pub  <url> <qos> <topic>  <size_of_packets> <number_of_packets> <msg_interval>\n", 
