import pyshark

def extract_quic_packets(pcap_file, role, ip_filter):
    cap = pyshark.FileCapture(pcap_file, display_filter=f'')
    packets = {}
    for packet in cap:
        print(packet)
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
        except AttributeError:
            continue  # Ignora pacotes sem quic.packet_number
    cap.close()
    return packets


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


def generate_mermaid(emqx_packets, client_packets):
    sequence = ["```mermaid", "sequenceDiagram"]
    loss_emqx_clinet = 0
    loss_client_emqx = 0
    send_emqx_client = 0
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
                send_emqx_client += 1
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
    sequence.append(f'  "Pacotes Enviados EMQX -> Cliente" : {send_emqx_client}')
    sequence.append(f'  "Pacotes Enviados Cliente -> EMQX" : {send_sucess_client_emqx}')
    sequence.append(f'  "Pacotes Perdidos EMQX -> Cliente" : {loss_emqx_clinet}')
    sequence.append(f'  "Pacotes Perdidos Cliente -> EMQX" : {loss_client_emqx}')
    sequence.append("```")
    sequence.append("##### Total of packets: " + str(total_packets))
    sequence.append("##### Total of packets EMQX: " + str(send_total_emqx))
    sequence.append("##### Total of packets Cliente: " + str(send_total_client))
    sequence.append("##### Total of packets sucess EMQX -> Cliente: " + str(send_emqx_client))
    sequence.append("##### Total of packets sucess Cliente -> EMQX: " + str(send_sucess_client_emqx))
    sequence.append("##### Total of packets lost EMQX -> Cliente: " + str(loss_emqx_clinet))
    sequence.append("##### Total of packets lost Cliente -> EMQX: " + str(loss_client_emqx))

    print("Pacotes total enviados EMQX -> Cliente", send_total_emqx)
    print("Pacotes total enviados Cliente -> EMQX", send_total_client)
    print("Pacotes total enviados sucess EMQX -> Cliente", send_emqx_client)
    print("Pacotes total enviados sucess Cliente -> EMQX", send_sucess_client_emqx)
    print("Pacotes total enviados lost EMQX -> Cliente", loss_emqx_clinet)
    print("Pacotes total enviados lost Cliente -> EMQX", loss_client_emqx)


    return '\n'.join(sequence)

def main(emqx_pcap, client_pcap, output_file):
    emqx_packets = extract_quic_packets(emqx_pcap, "EMQX", "172.18.0.2")
    client_packets = extract_quic_packets(client_pcap, "Cliente", "172.18.0.3")
    
    mermaid_diagram = generate_mermaid(emqx_packets, client_packets)
    
    with open(output_file, 'w') as f:
        f.write(mermaid_diagram)
    
    print(f"Diagrama Mermaid salvo em {output_file}")

if __name__ == "__main__":
    main("results/quic/captures/run-1-loss-50%-delay-20ms-n-10-s-100-i-1-q-0-emqx.pcap", "results/quic/captures/run-1-loss-50%-delay-20ms-n-10-s-100-i-1-q-0-client.pcap", "sequence_diagram.md")
