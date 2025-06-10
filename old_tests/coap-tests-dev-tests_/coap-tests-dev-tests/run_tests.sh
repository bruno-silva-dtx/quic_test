#!/bin/bash

# Help function
helpFunction() {
    echo ""
    echo "Usage: $0 -b <broker address> -t <transport> -n <number of messages> -s <size of messages> -i <message interval> -r <runs>"
    echo -e "\t-b Broker address"
    echo -e "\t-t Transport protocol (tcp, dtls, ws, wss)"
    echo -e "\t-n Number of messages"
    echo -e "\t-s Size of messages in bytes"
    echo -e "\t-i Interval between messages in seconds"
    echo -e "\t-r Number of test iterations"
    exit 1 # Exit script after printing help
}

# Cleanup function to kill background processes
cleanup() {
    echo "Cleaning up..."
    [[ -n $TCPDUMP_PID ]] && kill $TCPDUMP_PID 2>/dev/null
    [[ -n $CONSUMER_PID ]] && kill $CONSUMER_PID 2>/dev/null
    [[ -n $PRODUCER_PID ]] && kill $PRODUCER_PID 2>/dev/null
    echo "All processes terminated. Exiting."
}

# Trap SIGINT and SIGTERM to cleanup
trap cleanup SIGINT SIGTERM EXIT

# Argument parsing
while getopts "b:t:n:s:i:r:" opt; do
    case "$opt" in
        b ) broker="$OPTARG" ;;
        t ) transport="$OPTARG" ;;
        n ) number_of_messages="$OPTARG" ;;
        s ) size_of_messages="$OPTARG" ;;
        i ) message_interval="$OPTARG" ;;
        r ) runs="$OPTARG" ;;
        ? ) helpFunction ;;
    esac
done

# Check if all required parameters are filled
if [ -z "$broker" ] || [ -z "$transport" ] || [ -z "$number_of_messages" ] || [ -z "$size_of_messages" ] || [ -z "$message_interval" ] || [ -z "$runs" ]; then
    echo "Some or all of the parameters are empty"
    helpFunction
fi

# Fazer update 
sudo apt update
# Instalar o  libssl1.1
sudo apt install libssl1.1

# Execute tests the specified number of times
results_base_dir="./results"
mkdir -p "$results_base_dir"

# Criar diretórios de resultados específicos do teste antes de iniciar os testes
for (( run=1; run<=$runs; run++ ))
do
    transport_dir="$results_base_dir/$transport"
    mkdir -p "$transport_dir" # Certifica-se de que o diretório para o protocolo de transporte existe

    run_dir="$transport_dir/run-$run"
    mkdir -p "$run_dir" # Cria um diretório específico para cada execução de teste

    echo "Executing test $run for $transport..."
    
    # Inicia o tcpdump, consumidor e produtor como antes, mas assegura que os arquivos são escritos nos diretórios criados
    sudo timeout 30s tcpdump -U -i any -w "$run_dir/tcpdump.pcap" &
    TCPDUMP_PID=$!
    echo "tcpdump started with PID: $TCPDUMP_PID"

    # Inicia o consumidor e produtor, garantindo que os logs vão para o diretório correto
    timeout 30s python3 test_consumer.py > "$run_dir/consumer.log" 2>&1 &
    CONSUMER_PID=$!
    echo "Consumer started with PID: $CONSUMER_PID"

    timeout 30s python3 test_producer.py -b "$broker" -t "$transport" -n "$number_of_messages" -s "$size_of_messages" -i "$message_interval" > "$run_dir/producer.log" 2>&1 &
    PRODUCER_PID=$!
    echo "Producer started with PID: $PRODUCER_PID"

    # Espera o consumidor e produtor terminarem
    wait $CONSUMER_PID
    echo "Consumer process completed."
    wait $PRODUCER_PID
    echo "Producer process completed."

    echo "Test $run for $transport completed."
done

echo "All tests have been completed."
cleanup