#!/bin/bash

# Valores de taxa de perda de pacotes (em %)
loss_values=(1 5 10 25)

# Configurações fixas
runs=10
delay="20ms"
jitter="5ms"
num_messages=100
message_size=1500
interval=1

for qos_level in 1 2
do
  echo "Testing with QoS level: ${qos_level}"

  for loss in "${loss_values[@]}"
  do
    echo "Running test with packet loss: ${loss}%, QoS: ${qos_level}"
    echo "Received parameters: $runs, $loss, 25%, $delay, $jitter, $num_messages, $message_size, $interval, $qos"
    ./run_tests.sh -r $runs -l ${loss}% -p 25% -d $delay -j $jitter -n $num_messages -s $message_size -i $interval -q $qos_level
    sleep 10
  done

  # Renomeia a pasta de resultados após cada nível de QoS
  if [ -d ./results ]; then
    mv ./results ./results_qos_${qos_level}
    echo "Renamed ./results to ./results_qos_${qos_level}"
  else
    echo "Warning: ./results directory not found after QoS $qos_level"
  fi

done
