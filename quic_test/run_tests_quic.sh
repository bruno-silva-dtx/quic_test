
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
sleep 10

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


sudo docker run -d --name quic_test --network=quic_test_emqx-bridge quic_mqtt tail -f /dev/null

docker cp send_msg_quic.sh quic_test:/root/NanoSDK/extern/msquic



# Run the tests
for (( x=1; x<=$runs; x++ )); do


      echo "Correndo teste $x"

      docker exec quic_test bash -c "
         apt install sudo -y && \
         sudo apt-get install -y build-essential git pkg-config autoconf automake libtool -y && \
         sudo apt-get install -y liblttng-ust-dev libbabeltrace-dev liburcu-dev -y && \
         sudo apt-get install lttng-tools lttng-modules-dkms lttng-ust lttng-tools -y && \
         cd /root/NanoSDK/extern/msquic && \
         chmod +x scripts/log_wrapper.sh  && \
         chmod +x send_msg_quic.sh && \
         ./scripts/log_wrapper.sh ./send_msg_quic.sh 0 topic $size_of_packets $number_of_packets $msg_interval > log_tracer_${loss}_${delay}_${number_of_packets}_${msg_interval}_${qos}_${x}.log 
         "  

        sleep 10 
      docker exec quic_test bash -c " 
         echo 'Correu o send_msg_quic.sh' && \
         apt install --no-install-recommends -y dotnet-runtime-6.0 dotnet-sdk-6.0 dotnet-host && \
         git submodule update --init submodules/clog && \
         dotnet build submodules/clog/src/clog2text/clog2text_lttng/ -c Release
      "
   # ./scripts/log_wrapper.sh  ./send_msg_quic.sh 0 topic 100 10 10

      sleep 15

      docker exec quic_test bash -c "
            cd /root/NanoSDK/extern/msquic && \
            echo 'babeltrace --names all ./msquic_lttng*/* > quic.babel.txt' && \
            apt update && \
            dotnet build submodules/clog/src/clog2text/clog2text_lttng/ -c Release && \
            babeltrace --names all ./msquic_lttng*/* > quic.babel.txt
         "     
      sleep 5


       docker exec quic_test bash -c "
            cp /root/NanoSDK/extern/msquic/src/manifest/clog.sidecar /root/NanoSDK/extern/msquic && \
            chmod +x /root/NanoSDK/extern/msquic/submodules/clog/src/clog2text/clog2text_lttng/bin/Release/net6.0/clog2text_lttng && \
            ./submodules/clog/src/clog2text/clog2text_lttng/bin/Release/net6.0/clog2text_lttng -i quic.babel.txt -s clog.sidecar -o quic.log --showTimestamp --showCpuInfo && \
            mv quic.babel.txt log_msquic_${loss}_${delay}_${number_of_packets}_${msg_interval}_${qos}_${x}.log
         "
      sleep 5

    # Copy logs to host
      docker cp quic_test:/root/NanoSDK/extern/msquic/log_tracer_${loss}_${delay}_${number_of_packets}_${msg_interval}_${qos}_${x}.log ./results/quic/
      docker cp quic_test:/root/NanoSDK/extern/msquic/log_msquic_${loss}_${delay}_${number_of_packets}_${msg_interval}_${qos}_${x}.log ./results/quic/
   
    sleep 1
    # Clean up inside the container
    docker exec quic_test bash -c "
      cd /root/NanoSDK/extern/msquic && \
      rm -r log_* && \
      rm -r ./msquic_lttng* && \
      lttng destroy -a 
    "


    sleep 5

    # Terminate tcpdump
    #pid=$(pgrep tcpdump)  
    #sudo kill -2 "$pid"
done

# Clean up tc
sudo tc qdisc del dev "$veth" root
sudo tc qdisc del dev "$veth" handle ffff: ingress
sudo modprobe -r ifb

# Clean up docker
docker compose down
docker system prune -f