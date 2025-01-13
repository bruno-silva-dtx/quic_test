#!/bin/bash

helpFunction()
{
   echo ""
   echo "Usage: $0 -r <runs> -l <loss> -p <burst loss probability> -d <delay> -j <delay std dev> -n <number of messages> -s <size of messages> -i <message interval> -q <QoS level>"
   echo -e "\t-r number of times to run each test"
   echo -e "\t-l link loss probability"
   echo -e "\t-p link burst loss probability"
   echo -e "\t-d link delay"
   echo -e "\t-j link delay std dev - defines a jitter with normal distribution"
   echo -e "\t-n number of messages sent to broker"
   echo -e "\t-s size of messages sent to broker in bytes"
   echo -e "\t-i interval between consecutive messages sent to broker in seconds"
   echo -e "\t-q QoS level (0, 1, or 2)"
   echo -e "Example usage:"
   echo -e "$0 -r 10 -l 1% -p 25% -d 20ms -j 5ms -n 10 -s 100 -i 1 -q 1"
   echo -e "$0 -r 10 -l 0 -p 0 -d 20ms -j 5ms -n 10 -s 100 -i 1 -q 0"
   echo -e "$0 -r 1 -l 0 -p 0 -d 20ms -j 5ms -n 1 -s 100 -i 1 -q 0"
   echo -e "$0 -r 1 -l 30% -p 0% -d 20ms -j 5ms -n 100 -s 100 -i 300 -q 0"
   exit 1 # Exit script after printing help
}

while getopts "r:l:p:d:j:n:s:i:q:" opt
do
   case "$opt" in
      r ) runs="$OPTARG" ;;
      l ) loss="$OPTARG" ;;
      p ) burstloss="$OPTARG" ;;
      d ) delay="$OPTARG" ;;
      j ) delaystddev="$OPTARG" ;;
      n ) number_of_packets="$OPTARG" ;;
      s ) size_of_packets="$OPTARG" ;;
      i ) msg_interval="$OPTARG" ;;
      q ) qos="$OPTARG" ;;  # Adiciona a opção -qos
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$runs" ] || [ -z "$loss" ] || [ -z "$burstloss" ] || [ -z "$delay" ] || [ -z "$delaystddev" ] || [ -z "$number_of_packets" ] || [ -z "$size_of_packets" ] || [ -z "$msg_interval" ] || [ -z "$qos" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Aqui você pode adicionar código adicional para validar o valor do QoS se necessário
if [[ "$qos" != "0" && "$qos" != "1" && "$qos" != "2" ]]; then
   echo "Invalid QoS level. It must be 0, 1, or 2."
   exit 1
fi


# Start Docker environment
docker compose up -d
container_id=$(docker compose ps -q)
docker update --cpus="4.0" --memory="2.5g" --memory-swap="3g" emqx
#docker compose -f mqtt-receive.yml up -d
#container_receive=$(docker compose -f mqtt-receive.yml ps -q)
sleep 3

# Setup network conditions
iflink=$(docker exec -it $container_id bash -c 'cat /sys/class/net/eth0/iflink') 
iflink=$(echo $iflink | tr -d '\r') # Só caso tenha valor que não intressa # Identificador da interface de rede no host
veth=$(grep -l $iflink /sys/class/net/veth*/ifindex)  # Arquivos representam as interfaces no host (o id iflink tem que estar presente no arquivos) corresponde a interface do container, retorna todos com o grep
veth=$(echo $veth | sed -e 's;^.*net/\(.*\)/ifindex$;\1;') # Apenas queremos o nome da interface, não o caminho completo, veth##, o # é estraido
echo $container_id:$veth # Imprime o identificador do container, e o nome da interface de rede  

# the tc only affects egress queue we have to add an interface for ingress queue
# sudo ip link add ifb0 type ifb
sudo modprobe ifb # Útil para manipular o tráfego de entrada, já que o tc normalmente só manipula o tráfego de saída
sudo ip link add ifb0 type ifb # -> Isto está correto?
sudo ip link set dev ifb0 up # Criar ou carregar uma interface, é necessário ativá-la para que ela comece a funcionar

sudo tc qdisc add dev $veth ingress # Adiconar a disciplina da fila ingress
sudo tc filter add dev $veth parent ffff: protocol ip u32 match u32 0 0 flowid 1:1 action mirred egress redirect dev ifb0
# Adiciona filtro u32 match u32 0 0 é uma regra que corresponde a todos os pacotes espelha o tráfego de entrada para a interface 

# add delay and loss on both ingress and egress if's
sudo tc qdisc add dev $veth root netem delay $delay $delaystddev loss $loss $burstloss
sudo tc qdisc add dev ifb0 root netem delay $delay $delaystddev loss $loss $burstloss
sudo tc qdisc list

mkdir -p ./results/quic
mkdir -p ./results/quic/captures



sudo docker run -d --name quic_test --network=quic_test_emqx-bridge quic_test tail -f /dev/null

docker exec quic_test bash -c "
            pwsh ./root/NanoSDK/extern/msquic/scripts/prepare-machine.ps1 -ForTest -Tls openssl -Force -InitSubmodules
            cd /root/NanoSDK/extern/msquic && rm -rf build && mkdir -p build && cd build && cmake -D QUIC_ENABLE_LOGGING=ON -D QUIC_LOGGING_TYPE=stdout .. && make && make install           
            "
docker cp send_msg_quic.sh quic_test:/root/NanoSDK/extern/msquic
docker cp quic_api.c quic_test:/root/NanoSDK/src/supplemental/quic


      #sleep 5
#docker exec quic_test bash -c 'cd /root/NanoSDK/extern/msquic && rm -rf build && mkdir -p build && cd build && cmake -D QUIC_ENABLE_LOGGING=ON -D QUIC_LOGGING_TYPE=stdout .. && make && make install && cd /root/NanoSDK/demo/quic_mqtt && rm -rf build && mkdir -p build && cd build && cmake -D QUIC_ENABLE_LOGGING=ON -D QUIC_LOGGING_TYPE=stdout .. && make && make install && cd /root/NanoSDK/demo/quic_mqtt && rm -rf build && mkdir -p build && cd build && cmake .. && make && make install'
   
for (( x=1; x<=$runs; x++ )); do
      sleep 3
      echo "Correndo teste $x"
      sudo tcpdump -U -i $veth port 14567 -w ./results/quic/captures/run-$x-loss-$loss-delay-$delay-n-$number_of_packets-s-$size_of_packets-i-$msg_interval-q-$qos.pcap &
      TCPDUMP_PID=$!
      sleep 3

      docker exec quic_test bash -c "
         apt install sudo -y && \
         apt full-upgrade -y && \
         apt autoremove
      "
      
      docker exec quic_test bash -c "
         cd /root/NanoSDK/extern/msquic && \
         chmod +x scripts/log_wrapper.sh  && \
         chmod +x send_msg_quic.sh && \
         ./scripts/log_wrapper.sh ./send_msg_quic.sh 0 topic $size_of_packets $number_of_packets $msg_interval > log_tracer_${loss}_${delay}_${number_of_packets}_${msg_interval}_${qos}_${x}.log 
         sleep 30
         "  
      #   lttng destroy -a  && ./scripts/log_wrapper.sh  ./send_msg_quic.sh 0 topic 100 10 10   && babeltrace --names all ./msquic_lttng*/* > quic.babel.txt %% cat quic.babel.txt
      sleep 10
      docker exec quic_test bash -c " 
         cd /root/NanoSDK/extern/msquic && \
         echo 'Correu o send_msg_quic.sh' && \
         git submodule update --init submodules/clog && \
         dotnet build submodules/clog/src/clog2text/clog2text_lttng/ -c Release
      "
   # ./scripts/log_wrapper.sh  ./send_msg_quic.sh 0 topic 100 10 10


      docker exec quic_test bash -c "
            cd /root/NanoSDK/extern/msquic && \
            apt update && \
            dotnet build submodules/clog/src/clog2text/clog2text_lttng/ -c Release && \
            babeltrace --names all ./msquic_lttng*/* > quic.babel.txt
         "     


      docker exec quic_test bash -c "
            cd /root/NanoSDK/extern/msquic && \
            cp /root/NanoSDK/extern/msquic/src/manifest/clog.sidecar /root/NanoSDK/extern/msquic && \
            chmod +x /root/NanoSDK/extern/msquic/submodules/clog/src/clog2text/clog2text_lttng/bin/Release/net6.0/clog2text_lttng && \
            submodules/clog/src/clog2text/clog2text_lttng/bin/Release/net6.0/clog2text_lttng -i quic.babel.txt -s clog.sidecar -o log_msquic_${loss}_${delay}_${number_of_packets}_${msg_interval}_${qos}_${x}.log --showTimestamp --showCpuInfo 
         "
      sleep 5

    # Copy logs to host
      # Copiar os arquivos de log do contêiner para o host
      docker cp quic_test:/root/NanoSDK/extern/msquic/log_tracer_${loss}_${delay}_${number_of_packets}_${msg_interval}_${qos}_${x}.log ./results/quic/log_tracer-$x-loss-$loss-delay-$delay-n-$number_of_packets-s-$size_of_packets-i-$msg_interval-q-$qos.log
      docker cp quic_test:/root/NanoSDK/extern/msquic/log_msquic_${loss}_${delay}_${number_of_packets}_${msg_interval}_${qos}_${x}.log ./results/quic/log_msquic-$x-loss-$loss-delay-$delay-n-$number_of_packets-s-$size_of_packets-i-$msg_interval-q-$qos.log
      docker cp quic_test:/tmp/SslKeyLogFile_cb  ./results/quic/SslKeyLogFile-$x-loss-$loss-delay-$delay-n-$number_of_packets-s-$size_of_packets-i-$msg_interval-q-$qos.txt


      docker exec quic_test bash -c "
         cd /root/NanoSDK/extern/msquic && \
         rm -r log_* && \
         rm -r ./msquic_lttng* && \
         rm -r ./tmp/SslKeyLogFile_cb && \
         lttng destroy -a 
      "
done

# Clean up tc
sudo tc qdisc del dev "$veth" root
sudo tc qdisc del dev "$veth" handle ffff: ingress
sudo modprobe -r ifb

# Clean up docker
docker stop quic_test quic_test_receiver
docker rm quic_test quic_test_receiver
docker compose down
docker system prune -f
