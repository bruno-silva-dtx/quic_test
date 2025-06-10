
from dataclasses import dataclass
import hashlib
import pyshark
import pandas as pd
import os
import argparse
import json

# Estrutura de dados para armazenar informações do pacote
@dataclass
class Packet:
    id: str
    src_ip: str
    dst_ip: str
    timestamp: float
    
def extract_quic_packets(pcap_file: str, role: str):
    cap = pyshark.FileCapture(pcap_file, display_filter='quic')
    packets = []
    total_bytes = 0
    total_packets = 0
    for packet in cap:
        total_packets += 1
        total_bytes += int(packet.length)
        layer_data = {}
        hash_func = hashlib.sha256()
      
        for layer in packet.layers:
            if   layer.layer_name == "quic":  # Ignorar a camada frame
                pass  
            else:
                for field in layer._all_fields.values():
                    layer_data[layer.layer_name] = {
                            field.name: field.show 
                        for field in layer._all_fields.values() 
                            if field.name not in ["udp.time_relative", "udp.time_delta"]
                }
        hash_func.update(json.dumps(layer_data, sort_keys=True).encode())
        id_hex = hash_func.hexdigest()
        # Criar o ID do pacote para comparação  
        pkt = Packet(
            id=layer_data,
            src_ip=packet.ip.src,
            dst_ip=packet.ip.dst,
            timestamp=float(packet.sniff_time.timestamp())
        )
        packets.append(pkt)

    cap.close()
    return packets , total_bytes , total_packets


def identify_losses(emqx_packets, client_packets):
   
    # Sequence of packets
    send_success_client_to_emqx = 0
    send_success_emqx_to_client = 0
    loss_emqx_client = 0
    loss_client_emqx = 0

    #Total packet by role
    send_total_emqx = len(emqx_packets)
    send_total_client = len(client_packets)
    # Total packets 
    total_packets = send_total_emqx + send_total_client


   # Interjoin packets emqx_packets and client_packets
    inter_join_packets = []
    diff_packets = {}

    send_sucess_total = 0
    send_fail_total = 0

    for pkt_emqx in emqx_packets:        
        for pkt_client in client_packets:
            if pkt_emqx.id == pkt_client.id:
                inter_join_packets.append(pkt_emqx)
                break
            else:
                send_fail_total += 1
                for layer, data_emqx in pkt_emqx.id.items():
                    if layer in pkt_client.id:
                        data_client = pkt_client.id[layer]
                        for field_name, emqx_value in data_emqx.items():
                            client_value = data_client.get(field_name)
                            if emqx_value != client_value:
                                diff_key = (layer, field_name)
                                diff_packets[diff_key] = diff_packets.get(diff_key, 0) + 1

    

    # Total send sucess packets
    send_sucess_total = 0
    send_fail_total = 0

    send_sucess_total = len(inter_join_packets)

    top_diff_packets = sorted(diff_packets.items(), key=lambda x: x[1], reverse=True)[:10]

    all_packets = sorted(emqx_packets + client_packets, key=lambda pkt: pkt.timestamp)

    diff_packets = {}

    assert len(all_packets) == total_packets
    
    pacote_perdido = None

    for pkt in emqx_packets:
        if pkt.id in [p.id for p in inter_join_packets]:  # Criando uma lista temporária
            send_success_emqx_to_client += 1
        else:
            loss_emqx_client += 1
    for pkt in client_packets:
        if pkt.id in [p.id for p in inter_join_packets]:  # Criando uma lista temporária
            send_success_client_to_emqx += 1
        else:
            loss_client_emqx += 1

    return send_total_emqx, send_total_client, send_success_emqx_to_client, send_success_client_to_emqx, loss_emqx_client, loss_client_emqx

def analyze_pcap_files(directory, output_file):
    results = []

    paired_files = {}
    for filename in os.listdir(directory):
        if filename.endswith(".pcap"):
            base_name = "-".join(filename.split("-")[:-1])
            role = "client" if "client" in filename else "emqx"

            if base_name not in paired_files:
                paired_files[base_name] = {}
            paired_files[base_name][role] = os.path.join(directory, filename)
    
    for base_name, files in paired_files.items():
        if "client" in files and "emqx" in files:
            parts = base_name.split("-")
            run_x = parts[1]
            loss = parts[3]
            num_msgs = parts[7]
            msg_interval = parts[5]
            qos = parts[13]
            
            try:
                emqx_packets = extract_quic_packets(files["emqx"], "EMQX")
                print(f"Processando arquivos: {files['emqx']} e {files['client']}")
                client_packets , total_bytes , total_packets = extract_quic_packets(files["client"], "Cliente")
                print(f"Total de bytes: {total_bytes}, Total de pacotes: {total_packets}")
            except Exception as e:
                print(f"Erro ao processar os arquivos {files['emqx']} e {files['client']}: {e}")
                continue

            send_total_emqx, send_total_client, send_success_emqx_to_client, send_success_client_to_emqx, loss_emqx_client, loss_client_emqx = identify_losses(emqx_packets[0], client_packets)

            
            results.append({
                "Run_X": run_x,
                "Loss": loss,
                "Number_of_Msg": num_msgs,
                "Message_Interval": msg_interval,
                "QoS": qos,
                "Total_Packets": total_packets,
                "Total_Bytes": total_bytes,
                "Total_loss_client_emqx": loss_client_emqx,
                "Total_loss_emqx_client": loss_emqx_client,
            })
    
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)  # Alterado para salvar como CSV


def main():
    parser = argparse.ArgumentParser(description="Análise de capturas QUIC.")
    parser.add_argument(
        "-d", "--directory",
        default="results/quic/captures/",
        help="Diretório contendo os arquivos .pcap"
    )
    parser.add_argument(
        "-o", "--output",
        default="quic_analysis.csv",
        help="Nome do arquivo CSV de saída"
    )
    args = parser.parse_args()

    analyze_pcap_files(args.directory, args.output)

if __name__ == "__main__":
    main()
