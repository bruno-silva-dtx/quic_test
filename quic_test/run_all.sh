#!/bin/bash

# Valores de taxa de perda de pacotes (em %)
loss_values=(0)
# Configurações fixas   0.1 1 5 10 25
runs=10
delay="20ms"
jitter="5ms"
num_messages=1000
message_size=2500
interval=100


for qos_level in  0 
do
  echo "Testing with QoS level: ${qos_level}"

  # Loop para rodar o script com diferentes taxas de perda
  for loss in "${loss_values[@]}"
  do
    echo "Running test with packet loss: ${loss}%, QoS: ${qos_level}"
    echo "./run_tests_quic.sh -r $runs -l $loss% -p 25% -d $delay -j $jitter -n $num_messages -s $message_size -i $interval -q $qos_level"
    ./run_tests_quic.sh -r $runs -l ${loss}% -p 25% -d $delay -j $jitter -n $num_messages -s $message_size -i $interval -q $qos_level
    sleep 10
  done

done
