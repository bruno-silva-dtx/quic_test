#!/bin/bash

# Valores de taxa de perda de pacotes (em %)
loss_values=(0 0.1 1 5 10 25)
# Configurações fixas
runs=10
delay="20ms"
jitter="5ms"
num_messages=100
message_size=1500
interval=1
qos_level=0

# Loop para rodar o script com diferentes taxas de perda
for loss in "${loss_values[@]}"
do
  echo "Running test with packet loss: ${loss}%"
  ./run_tests_quic.sh -r $runs -l "$loss%" -p 25% -d $delay -j $jitter -n $num_messages -s $message_size -i $interval -q $qos_level
  sleep 10
done
