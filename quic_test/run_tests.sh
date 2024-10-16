
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


# docker build do quic client 
# docker build -f Dockerfile -t quic-client:0.1 .

# Run the tests
x=1
while [ $x -le $runs ]
do
    # Adjust the port according to the QUIC client (usually 4433 or specified by the implementation)
    #sudo tcpdump -U -i $veth port 14567 -w ./results/quic/run-$x-loss-$loss-delay-$delay-n-$number_of_packets-s-$size_of_packets-i-$msg_interval-q-$qos.pcap &
    #sleep 5

   #sudo tcpdump -U -i $veth -w ./results/quic/run-$x-loss-$loss-delay-$delay-n-$number_of_packets-s-$size_of_packets-i-$msg_interval-q-$qos-test.pcap &
    #sleep 5
    
    #Futura implmentação que pretendo:
    #docker run --network=mqtt-tests_emqx-bridge -it quic_client_test -b broker.emqx.io -p 4433 -n $number_of_packets -s $size_of_packets -i $msg_interval
      
    #sudo docker run --network=quic_test_emqx-bridge quic_client_test  ./quic_client pub 'mqtt-tcp://emqx:14567' $qos topic hello
    ## Correto para o teste de conexão, com SSLKEYLOGFILE, 
    #sudo docker run --network=quic_test_emqx-bridge \
    # -e SSLKEYLOGFILE="/tmp/SSLKEYLOGFILE" \
   # --mount 'type=bind,source=/home/dae/quic_protocol/quic_test/quic_test,destination=/tmp/SSLKEYLOGFILE' \
   # quic_mqtt  ./quic_client pub 'mqtt-tcp://emqx:14567' $qos topic $size_of_packets $number_of_packets  $msg_interval
   
   
   #Corrrer infinitamente para debug
      sudo docker run --network=quic_test_emqx-bridge \
     -e SSLKEYLOGFILE="/tmp/SSLKEYLOGFILE" \
      --mount 'type=bind,source=/home/dae/quic_protocol/quic_test/quic_test,destination=/tmp/SSLKEYLOGFILE' \
      quic_mqtt tail -f /dev/null

   # ./NanoSDK/demo/quic_mqtt/build/quic_client pub 'mqtt-tcp://emqx:14567' 0 topic 100 100  10
   # sudo rm -r /NanoSDK/build 
   #mkdir /NanoSDK/build
   # cd /NanoSDK/build
   # cmake -DENABLE_LOG=ON  -DCMAKE_BUILD_TYPE=Debug .. 
   # sudo make
   # sudo make install
    
    #sudo docker run --network=quic_test_emqx-bridge \
     #-e SSLKEYLOGFILE="/tmp/SSLKEYLOGFILE" \
     #quic_mqtt  ./quic_client pub 'mqtt-tcp://emqx:14567' $qos topic $size_of_packets $number_of_packets  $msg_interval
  
sleep 5000000000
#   sudo docker run --rm --network="quic_test_emqx-bridge" \
#    -e SSLKEYLOGFILE="/tmp/sslkeylogfile.log" \
#    quic_mqtt ./quic_client pub "mqtt-tcp://emqx:14567" "$QOS" topico ola

    pid=$(ps -e | pgrep tcpdump)  
    #sleep 500
    sudo kill -2 $pid
    x=$(( $x + 1 ))
done


# Clean up tc
sudo tc qdisc del dev $veth root # Remove a disciplina de enfileiramento raiz 
sudo tc qdisc del dev $veth handle ffff: ingress
sudo modprobe -r ifb

# Clean up docker
docker compose down

docker system prune -f

