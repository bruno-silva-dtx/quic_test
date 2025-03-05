import subprocess

def count_quic_packets(pcap_file):
    """Conta pacotes QUIC num arquivo PCAP usando tshark"""
    cmd = [
        "tshark", "-r", pcap_file, "-Y", "quic", "-T", "fields", "-e", "frame.number"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return len(result.stdout.splitlines())

pcap_without_loss = "/home/bruno/Desktop/quic_test/quic_test/results/quic/captures/run-1-loss-25%-delay-20ms-n-50-s-100-i-1-q-0-client.pcap"
pcap_with_loss = "/home/bruno/Desktop/quic_test/quic_test/results/quic/captures/run-1-loss-25%-delay-20ms-n-50-s-100-i-1-q-0-emqx.pcap"

quic_packets_no_loss = count_quic_packets(pcap_without_loss)
quic_packets_loss = count_quic_packets(pcap_with_loss)

lost_packets = quic_packets_no_loss - quic_packets_loss
loss_percentage = (lost_packets / quic_packets_no_loss) * 100 if quic_packets_no_loss > 0 else 0

print(f"Pacotes QUIC sem perda: {quic_packets_no_loss}")
print(f"Pacotes QUIC com perda: {quic_packets_loss}")
print(f"Pacotes perdidos: {lost_packets}")
print(f"Perda percentual: {loss_percentage:.2f}%")


