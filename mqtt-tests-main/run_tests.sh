
helpFunction()
{
   echo ""
   echo "Usage: $0 -r <runs> -l <loss> -p <burst loss probability> -d <delay> -j <delay std dev> -n <number of messages> -s <size of messages> -i <message interval>"
   echo -e "\t-r number of times to run each test"
   echo -e "\t-l link loss probability"
   echo -e "\t-p link burst loss probability"
   echo -e "\t-d link delay"
   echo -e "\t-j link delay std dev - defines a jitter with normal distribution"
   echo -e "\t-n number of messages sent to broker"
   echo -e "\t-s size of messages sent to broker in bytes"
   echo -e "\t-i interval between consecutive messages sent to broker in seconds"
   echo -e "Example usage:"
   echo -e "$0 -r 10 -l 1% -p 25% -d 20ms -j 5ms -n 10 -s 100 -i 1"
   exit 1 # Exit script after printing help
}

while getopts "r:l:p:d:j:n:s:i:" opt
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
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$runs" ] || [ -z "$loss" ] || [ -z "$burstloss" ] || [ -z "$delay" ] || [ -z "$delaystddev" ] || [ -z "$number_of_packets" ] || [ -z "$size_of_packets" ] || [ -z "$msg_interval" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct

# runs=$1
# loss=$2 
# burstloss=$3
# delay=$4
# delaystddev=$5
# number_of_packets=$6
# size_of_packets=$7
# msg_interval=$8



# Run docker-compose
docker compose up -d
# Get the container IDs
container_id=$(docker compose ps -q)
sleep 10
# Loop through the container IDs
# for container_id in $container_ids; do
  # Get the veth associated with the container
  # veth=$(docker inspect -f '{{.NetworkSettings.SandboxKey}}' $container_id)
  
  # Print the container ID and the associated veth
  # echo "Container ID: $container_id"
  # echo "Associated veth: $veth"

iflink=`docker exec -it $container_id bash -c 'cat /sys/class/net/eth0/iflink'`
iflink=`echo $iflink|tr -d '\r'`
veth=`grep -l $iflink /sys/class/net/veth*/ifindex`
veth=`echo $veth|sed -e 's;^.*net/\(.*\)/ifindex$;\1;'`
echo $container_id:$veth

# the tc only affects egress queue we have to add an interface for ingress queue
sudo modprobe ifb
sudo ip link set dev ifb0 up
sudo tc qdisc add dev $veth ingress
sudo tc filter add dev $veth parent ffff: protocol ip u32 match u32 0 0 flowid 1:1 action mirred egress redirect dev ifb0

# add delay and loss on both ingress and egress if's
sudo tc qdisc add dev $veth root netem delay $delay $delaystddev loss $loss $burstloss
sudo tc qdisc add dev ifb0 root netem delay $delay $delaystddev loss $loss $burstloss
sudo tc qdisc list

mkdir -p ./results/tcp 
mkdir -p ./results/tls
mkdir -p ./results/ws 
mkdir -p ./results/wss 

docker build -f Dockerfile -t mqtt-pub:0.1 .

x=1
while [ $x -le $runs ]
do
    echo "Running test $x of $runs with loss $loss, delay $delay, number of packets $number_of_packets, size of packets $size_of_packets, and message interval $msg_interval"
    sudo tcpdump -U -i $veth port 1883 -w ./results/tcp/run-$x-loss-$loss-delay-$delay-n-$number_of_packets-s-$size_of_packets-i-$msg_interval.pcap &
    sleep 5
    docker run --network=mqtt-tests-main_emqx-bridge -it mqtt-pub:0.1 -b broker.emqx.io -t tcp -n $number_of_packets -s $size_of_packets -i $msg_interval
    pid=$(ps -e | pgrep tcpdump)  
    sleep 5
    sudo kill -2 $pid
    x=$(( $x + 1 ))   
done

x=1
while [ $x -le $runs ]
do
    sudo tcpdump -U -i $veth port 8883 -w ./results/tls/run-$x-loss-$loss-delay-$delay-n-$number_of_packets-s-$size_of_packets-i-$msg_interval.pcap &
    sleep 5
    docker run --network=mqtt-tests-main_emqx-bridge -it mqtt-pub:0.1 -b broker.emqx.io -t tls -n $number_of_packets -s $size_of_packets -i $msg_interval
    pid=$(ps -e | pgrep tcpdump)  
    sleep 5
    sudo kill -2 $pid
    x=$(( $x + 1 ))
done

#x=1
#while [ $x -le $runs ]
#do
#    sudo tcpdump -U -i $veth port 8083 -w ./results/ws/run-$x-loss-$loss-delay-$delay-n-$number_of_packets-s-$size_of_packets-i-$msg_interval.pcap &
#    sleep 5
#    docker run --network=mqtt-tests-main_emqx-bridge -it mqtt-pub:0.1 -b broker.emqx.io -t ws -n $number_of_packets -s $size_of_packets -i $msg_interval
#    pid=$(ps -e | pgrep tcpdump)  
#    sleep 5
#    sudo kill -2 $pid
#    x=$(( $x + 1 ))
#done
#
#x=1
#while [ $x -le $runs ]
#do
#    sudo tcpdump -U -i $veth port 8084 -w ./results/wss/run-$x-loss-$loss-delay-$delay-n-$number_of_packets-s-$size_of_packets-i-$msg_interval.pcap &
#    sleep 5
#    docker run --network=mqtt-tests-main_emqx-bridge -it mqtt-pub:0.1 -b broker.emqx.io -t wss -n $number_of_packets -s $size_of_packets -i $msg_interval
#    pid=$(ps -e | pgrep tcpdump)  
#    sleep 5
#    sudo kill -2 $pid
#    x=$(( $x + 1 ))
#done

# Clean up tc
sudo tc qdisc del dev $veth root
sudo tc qdisc del dev $veth handle ffff: ingress
sudo modprobe -r ifb

# Clean up docker
docker compose down

docker system prune -f
