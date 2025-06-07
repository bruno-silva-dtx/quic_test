from scapy.all import rdpcap
import os
import pandas as pd
import pyshark
import nest_asyncio

def process_pcap(pcap_file):
    pcap_flow = rdpcap(pcap_file)
    ip_len_sum = 0
    n_packets = 0
    for session in pcap_flow.sessions():
        packet_lists = pcap_flow.sessions()[session]
        n_packets += len(packet_lists)
        for packet in packet_lists:
             # packet.show()
            ip_len_sum += packet.getlayer('IP').len
    return n_packets, ip_len_sum

def process_pcap_v2(pcap_file):
    n_packets = 0
    total_bytes = 0
    print("Processing pcap file:", pcap_file)

    try:
        with pyshark.FileCapture(pcap_file, display_filter='ip') as pcap:
            print(f"-------> Reading {pyshark.FileCapture(pcap_file, display_filter='ip')}")
            for packet in pcap:
                print(f"---------------> Processing packet {n_packets + 1}: {packet}")
                total_bytes += int(packet.length)
                n_packets += 1
            total_bytes += int(packet.length)
            print(f"-------> Processed {n_packets} packets, total bytes: {total_bytes}")
    except Exception as e:
        print(f"Error reading ----------- {pcap_file}: {e}")
    return n_packets, total_bytes


def get_errors(pcap_file):
    pcap_errors = pyshark.FileCapture(pcap_file, display_filter='tcp.analysis.flags')
    ip_len_sum = 0
    n_packets = 0
    for packet in pcap_errors:
        n_packets += 1
        ip_len_sum += int(packet.ip.len)
    
    pcap_errors.close()
    return n_packets, ip_len_sum

def get_energy_and_deviation(perf_file):
    with open(perf_file, 'r') as f:
        for line in f:
            if 'energy-pkg' in line:
                line = line.replace(',','.')
                line = line.split(' ')
                line = list(filter(('').__ne__, line))
                f.close()
                return line[0], line[-2]
        else:
            f.close()
            return None, None
        
if __name__ == '__main__':
    transports = os.listdir('./results')
    pcap_results = []
    pcap_cols = None
    perf_results = []
    perf_cols = None
    for transport in transports:
        files = os.listdir('./results/{}'.format(transport))
        files.sort()
        print('Results for transport', transport)
        for file in files:
            if 'pcap' in file:
                pcap_file = './results/{}/{}'.format(transport, file)
                pcap = pyshark.FileCapture(pcap_file,  display_filter='ip')
                n_packets, ip_len_sum = (process_pcap_v2(pcap_file=pcap_file))
                print("n_packets: ", n_packets, "\tip_len_sum: ", ip_len_sum)
                print('File: ', pcap_file)
                error_n_packets, error_ip_len_sum = get_errors(pcap_file=pcap_file)
                print('Total of packets: ', n_packets, '\tTotal of bytes: ', ip_len_sum, '\nError packets: ', error_n_packets, '\tError bytes: ', error_ip_len_sum)
                file = file.rstrip('.pcap')
                pcap_results.append([transport] + file.split('-')[1::2] +  [n_packets, ip_len_sum, error_n_packets, error_ip_len_sum])
                if pcap_cols is None:
                    pcap_cols = ['transport'] + file.split('-')[0::2] + ['Total packets', 'Total bytes', 'Error packets', 'Error bytes']

            elif 'perf' in file:
                perf_file = './results/{}/{}'.format(transport, file)
                energy, deviation = get_energy_and_deviation(perf_file)
                if energy and deviation:
                    energy = float(energy)
                    deviation = float(deviation.strip('+-%'))/100
                    print('File: ', perf_file)
                    print(f"Total energy: {energy} Joules {deviation}")
                file = file.rstrip('.txt')
                perf_results.append([transport] + file.split('-')[2::2] + [energy, deviation])
                print(perf_results)
                if perf_cols is None:
                    perf_cols = ['transport'] + file.split('-')[1::2] + ['energy', 'deviation']
            else:
                print('Unkown file: ', file)
        

    perf_results_pd = pd.DataFrame(perf_results, columns = perf_cols)
    nest_asyncio.apply()
    perf_results_pd.style
    print(perf_results_pd.to_string())
    perf_results_pd.to_csv('./perf_results.csv')

    pcap_results_pd = pd.DataFrame(pcap_results, columns = pcap_cols)

    pcap_results_pd.style
    print(pcap_results_pd.to_string())
    pcap_results_pd.to_csv('./pcap_results.csv')







