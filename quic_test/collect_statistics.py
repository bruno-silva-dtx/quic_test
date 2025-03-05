
import pyshark
import pandas as pd
import os




def extract_quic_packets(pcap_file : str, role, ip_filter):
    total_bytes = 0
    cap = pyshark.FileCapture(pcap_file, display_filter=f'')
    packets = {}
    for packet in cap:
        try:
            pkt_num = int(packet.quic.packet_number)
            id_ipv4 = (packet.ip.id  )
            src_ip = packet.ip.src
            dst_ip = packet.ip.dst
            src_port = packet.udp.srcport
            dst_port = packet.udp.dstport
            timestamp = float(packet.sniff_time.timestamp())
            unique_id = f"{src_ip}:{src_port}->{dst_ip}:{dst_port} #{pkt_num}-{str(id_ipv4)}"
            packets[unique_id] = timestamp
            if hasattr(packet, 'length'):  # Check if the packet has a length field
                total_bytes += int(packet.length)
        except AttributeError:
            continue  # Ignora pacotes sem quic.packet_number
    cap.close()
    return packets , total_bytes


def print_datagrams(pkt):
        src , pkt_info= pkt.split("->")
        dest_info, info= pkt_info.split("#")
        src , src_port = src.split(":")
        dest , dst_port = dest_info.split(":")
        pkt_num, frame_num = info.split("-")
        return src + '->' + dest + ': ' + info

def identify_packet(pkt):
        src , pkt_info= pkt.split("->")
        dest_info, info= pkt_info.split("#")
        src , src_port = src.split(":")
        dest , dst_port = dest_info.split(":")
        pkt_num, frame_num = info.split("-")
        return src , dest


def generate_mermaid(emqx_packets, client_packets,filename):
    sequence = ["```mermaid", "sequenceDiagram"]
    loss_emqx_clinet = 0
    loss_client_emqx = 0
    send_sucess_emqx_client = 0
    send_sucess_client_emqx = 0
    send_total_emqx= len(emqx_packets) 
    send_total_client= len(client_packets)
    send_total_client= len(client_packets)
    all_packets = {**emqx_packets, **client_packets}
    common_keys = set(emqx_packets.keys()) & set(client_packets.keys())
    print("Emqx quey")
    print(emqx_packets.keys())
    print("Client query")
    print(client_packets.keys())
    print(common_keys)
    inner_join_result = {key: (emqx_packets[key], client_packets[key]) for key in common_keys}
    print(inner_join_result)
    for pkt, timestamp in sorted(all_packets.items(), key=lambda x: x[1]):
        print(identify_packet(pkt))
        if pkt  in inner_join_result:
            print("Passou")
            if identify_packet(pkt)[0] == "172.18.0.3":
                sequence.append(f' Cliente->>EMQX: QUIC Packet {print_datagrams(pkt)} (Entregue)')
                send_sucess_client_emqx += 1
                print("Passou")
            else:
                sequence.append(f' EMQX->>Cliente: QUIC Packet {print_datagrams(pkt)} (Entregue)')
                send_sucess_emqx_client += 1
                print("Passou")
        if pkt not in inner_join_result:
            if identify_packet(pkt)[0] == "172.18.0.3":
                sequence.append(f' Cliente--xEMQX: QUIC Packet {print_datagrams(pkt)} (Perda)')
                loss_client_emqx += 1
            else:
                sequence.append(f' EMQX--xCliente: QUIC Packet {print_datagrams(pkt)} (Perda)')
                loss_emqx_clinet += 1

    print(loss_emqx_clinet)
    print(loss_client_emqx)
    total_packets = len(all_packets)
    sequence.append("```")
    sequence.append("```mermaid")
    sequence.append(f"pie")
    sequence.append(f'  "Pacotes Enviados EMQX -> Cliente" : {send_sucess_emqx_client}')
    sequence.append(f'  "Pacotes Enviados Cliente -> EMQX" : {send_sucess_client_emqx}')
    sequence.append(f'  "Pacotes Perdidos EMQX -> Cliente" : {loss_emqx_clinet}')
    sequence.append(f'  "Pacotes Perdidos Cliente -> EMQX" : {loss_client_emqx}')
    sequence.append("```")
    sequence.append("##### Total of packets: " + str(total_packets))
    sequence.append("##### Total of packets EMQX: " + str(send_total_emqx))
    sequence.append("##### Total of packets Cliente: " + str(send_total_client))
    sequence.append("##### Total of packets sucess EMQX -> Cliente: " + str(send_sucess_emqx_client))
    sequence.append("##### Total of packets sucess Cliente -> EMQX: " + str(send_sucess_client_emqx))
    sequence.append("##### Total of packets lost EMQX -> Cliente: " + str(loss_emqx_clinet))
    sequence.append("##### Total of packets lost Cliente -> EMQX: " + str(loss_client_emqx))

    print("Pacotes total enviados EMQX -> Cliente", send_total_emqx)
    print("Pacotes total enviados Cliente -> EMQX", send_total_client)
    print("Pacotes total enviados sucess EMQX -> Cliente", send_sucess_emqx_client)
    print("Pacotes total enviados sucess Cliente -> EMQX", send_sucess_client_emqx)
    print("Pacotes total enviados lost EMQX -> Cliente", loss_emqx_clinet)
    print("Pacotes total enviados lost Cliente -> EMQX", loss_client_emqx)



    with open(filename, "w") as file:
        for line in sequence:
            file.write(line + "\n")
    
    return total_packets , send_total_emqx, send_total_client, send_sucess_emqx_client, send_sucess_client_emqx, loss_emqx_clinet, loss_client_emqx

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
            loss = parts[2].split("%")[0]
            delay = parts[3].replace("ms", "")
            num_msgs = parts[4]
            msg_interval = parts[5]
            qos = parts[6]

            emqx_packets, total_bytes_emqx = extract_quic_packets(files["emqx"], "EMQX", "172.18.0.2")
            client_packets, total_bytes_client = extract_quic_packets(files["client"], "Cliente", "172.18.0.3")

            diagram_filename = os.path.join(directory, f"{base_name}-diagram.md")
            total_packets, send_total_emqx, send_total_client, send_sucess_emqx_client, send_sucess_client_emqx, loss_emqx_client, loss_client_emqx = generate_mermaid(
                emqx_packets, client_packets, diagram_filename
            )
            
            results.append({
                "Run_X": run_x,
                "Loss": loss,
                "Delay": delay,
                "Number_of_Msg": num_msgs,
                "Message_Interval": msg_interval,
                "QoS": qos,
                "SendTotalPackets_cliente": send_total_client,
                "SendTotalPackets_emqx": send_total_emqx,
                "Total_Send_Packets_EMQX_Client": send_sucess_emqx_client,
                "Total_Send_Packets_Client_EMQX": send_sucess_client_emqx,
                "Total_Losses_Send_by_CLIENT": loss_emqx_client,
                "Total_Losses_Send_by_EMQX": loss_client_emqx,
                "TotalBytesSent_EMQX": total_bytes_emqx,
                "TotalBytesSent_CLIENTE": total_bytes_client,
            })
    
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)  # Alterado para salvar como CSV

def main():
    directory = "results/quic/captures/"
    output_file = "quic_analysis.csv"
    analyze_pcap_files(directory, output_file)
    print(f"Resultados salvos em {output_file}")

if __name__ == "__main__":
    main()