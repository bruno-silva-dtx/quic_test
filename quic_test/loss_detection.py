import re
import csv
import sys
import os

def extract_log_data(log_file):
    print("Entrou na função",log_file)
    results = []  # Lista para armazenar resultados
    
    # Compilando a expressão regular para capturar o ProbeCount
    # Inicializa o contador
    try:
        probe_retransmit_count = 0
        file_name = log_file 
        with open(file_name, 'r') as log_file:
            for line in log_file:
                # Imprimindo a linha atual para depuração
                print(line.strip())  # strip() remove espaços em branco e quebras de linha

                # Contando as correspondências
                matches = re.findall(r"Probe Retransmit", line)
                print("Matcher =", matches)  # Mostra as correspondências encontradas
                probe_retransmit_count += len(matches)


            # Extraindo os parâmetros do nome do arquivo
        params = file_name.split('_')
        if len(params) >= 6:
            loss = params[2]
            delay = params[3]
            number_of_packets = params[4]
            msg_interval = params[5]
            qos = params[6].split('.')[0]  # Remove a extensão do arquivo
            x = params[7].split('.')[0] if len(params) > 7 else None  # Garante que 'x' existe

                # Adiciona os dados à lista
        if probe_retransmit_count is not None:  # Verifica se algum ProbeCount foi encontrado
                results.append([loss, delay, number_of_packets, msg_interval, qos, x, probe_retransmit_count])
        else:
                print(f"Número de parâmetros insuficiente no nome do arquivo '{log_file}'.")  # Mensagem de depuração
    except FileNotFoundError:
        print(f"Erro: O arquivo '{log_file}' não foi encontrado.")
    
    return results

def write_to_csv(data, output_file):
    header = ['Loss', 'Delay', 'Number of Packets', 'Message Interval', 'QoS', 'X', 'Count of Losses']
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)

def process_logs_in_directory(directory, output_file):
    all_results = []

    # Itera sobre todos os arquivos no diretório
    for filename in os.listdir(directory):
        if filename.endswith('.log'):  # Verifica se é um arquivo de log
            log_file_path = os.path.join(directory, filename)
            print(f"Extraindo dados de '{log_file_path}'...")
            log_data = extract_log_data(log_file_path)
            all_results.extend(log_data)  # Adiciona os dados extraídos à lista total

    write_to_csv(all_results, output_file)
    print(f"Todos os dados extraídos e salvos em '{output_file}' com sucesso.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python extract_log_data.py <caminho_para_diretorio> <caminho_para_output_csv>")
        sys.exit(1)

    directory = sys.argv[1]
    output_file = sys.argv[2]

    process_logs_in_directory(directory, output_file)
