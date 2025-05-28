
from dataclasses import dataclass
import pyshark
import pandas as pd
import os
import hashlib
import json
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
    for packet in cap:
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
        
        pkt = Packet(
            id=id_hex,
            src_ip=packet.ip.src,
            dst_ip=packet.ip.dst,
            timestamp=float(packet.sniff_time.timestamp())
        )
        packets.append(pkt)

    cap.close()
    return packets , total_bytes


def generate_mermaid(emqx_packets, client_packets,filename, local_diagram):
    sequence = ["```mermaid", "sequenceDiagram"]
    
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

    # Total send sucess packets
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


    #print(diff_packets)
    # Total send sucess packets
    send_sucess_total = len(inter_join_packets)
    print("Sucesso no interjoin:",send_sucess_total)



    # in case de compare packets layer by layer                          
    # print("Tamanho do Interjoin",len(inter_join_packets))
    # print("Diff Packetslayer_data",diff_packets)
    # # TOP 10 diff packets
    


        
    top_diff_packets = sorted(diff_packets.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top Diff Packets",top_diff_packets)   

    all_packets = sorted(emqx_packets + client_packets, key=lambda pkt: pkt.timestamp)

    diff_packets = {}

    assert len(all_packets) == total_packets
    
    #for pkt in all_packets:
    #     if pkt in inter_join_packets:
    #         if pkt.src_ip == "172.18.0.3":
    #             sequence.append(f' Cliente->>EMQX: QUIC Packet {pkt.id} (Entregue)')
    #         else:
    #             sequence.append(f' EMQX->>Cliente: QUIC Packet {pkt.id} (Entregue)')
    #     else:
    #         if pkt.src_ip == "172.18.0.3":
    #             sequence.append(f' Cliente--xEMQX: QUIC Packet {pkt.id} (Perda)')
    #         else:
    #             sequence.append(f' EMQX--xCliente: QUIC Packet {pkt.id} (Perda)')
    #sequence.append("```")

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

    
    sequence.append("total_send" + str(total_packets))
    sequence.append("send_total_emqx" + str(send_total_emqx))
    sequence.append("send_total_client" + str(send_total_client))
    sequence.append("send_sucess_emqx_client" + str(send_success_emqx_to_client))
    sequence.append("send_sucess_client_emqx" + str(send_success_client_to_emqx))
    sequence.append("loss_emqx_client" + str(loss_emqx_client))
    sequence.append("loss_client_emqx" + str(loss_client_emqx))
    sequence.append("tota_sucess_send" + str(send_sucess_total))
    sequence.append("total_loss_send" + str(send_fail_total))




    filename_final = local_diagram + filename
    with open(filename_final, "w") as file:
        for line in sequence:
            file.write(line + "\n")
    
    return total_packets, send_total_emqx, send_total_client, send_success_emqx_to_client, send_success_client_to_emqx, loss_emqx_client, loss_client_emqx
def analyze_pcap_files(directory, output_file, local_diagram=""):
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
            print(f"Analisando {base_name}")



            emqx_packets , total_bytes_emqx = extract_quic_packets(files["emqx"], "EMQX")
            client_packets , total_bytes_client = extract_quic_packets(files["client"], "Cliente")

            total_packets, send_total_emqx, send_total_client, send_success_emqx_to_client, send_success_client_to_emqx, loss_emqx_client, loss_client_emqx = generate_mermaid(emqx_packets, client_packets, f"{base_name}-diagram.md", local_diagram)
            print(f"Interseção de pacotes: {send_total_emqx}")
            print(f"Pacotes enviados Cliente: {send_total_client}")
            print(f"Pacotes entregues Cliente -> EMQX: {send_success_client_to_emqx}")
            print(f"Pacotes perdidos Cliente -> EMQX: {loss_client_emqx}")

            results.append({
                "Run_X": run_x,
                "Loss": loss,
                "Number_of_Msg": num_msgs,
                "Message_Interval": msg_interval,
                "QoS": qos,
                "Total_Packets": total_packets,
                "Total_Packets_Client": send_total_client,
                "Total_Packets_EMQX": send_total_emqx,
                "Total_send_success_client_to_emqx": send_success_client_to_emqx,
                "Total_send_success_emqx_to_client": send_success_emqx_to_client,
                "Total_loss_client_emqx": loss_client_emqx,
                "Total_loss_emqx_client": loss_emqx_client,
                "Total_bytes_emqx": total_bytes_emqx,
                "Total_bytes_client": total_bytes_client
            })
    
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)  # Alterado para salvar como CSV

def main():
    directory = "results_multi_stream/quic/captures/"
    output_file = "quic_analysis.csv"
    local_diagram = "results_multi_stream/quic/captures/"
    analyze_pcap_files(directory, output_file, local_diagram)
    print(f"Resultados salvos em {output_file}")

if __name__ == "__main__":
    main()