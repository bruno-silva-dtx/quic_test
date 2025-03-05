import re
import csv
import sys
import os


def extract_log_trace(log_file):
    pass
    results = []  # Lista para armazenar resultados
    
    # Compilando a expressão regular para capturar o ProbeCount
    # Inicializa o contador
    try:
        Totalbytessent = 0
        TotalUDPsendAPI = 0

        file_name = log_file 
        with open(file_name, 'r') as log_file:
            for line in log_file:
                pass
                findTotalbytessent = re.findall(r"Total bytes sent by applications: (\d+)", line)
                findTotalUDPsendAPI = re.findall(r"Total UDP send API calls: (\d+)", line)
                
                if findTotalbytessent:
                    Totalbytessent = int(findTotalbytessent[0])
                if findTotalUDPsendAPI:
                    TotalUDPsendAPI = int(findTotalUDPsendAPI[0])

            results.append([Totalbytessent, TotalUDPsendAPI])
            return results
    except FileNotFoundError:
        pass
    
    return results


def extract_log_msquic(log_file):
    pass
    results = []  # Lista para armazenar resultados
    
    try:
        SendTotalPackets = 0
        SendSuspectedLostPackets = 0
        SendSpuriousLostPackets = 0
        Loss_Ratio_RACK_FACK = 0    
        contLostPackets = 0
        contador_Rack = 0
        contador_Fack = 0
        RelacaoLost = 0
        Forgetting = 0
        Loss_Ratio_RACK_FACK_FORGETTING = 0

        file_name = log_file 
        with open(file_name, 'r') as log_file:
            for line in log_file:
                pass
                
                # Extrair os dados relevantes
                findSendTotalPackets = re.findall(r"SendTotalPackets=(\d+)", line)
                findSendSuspectedLostPackets = re.findall(r"SendSuspectedLostPackets=(\d+)", line)
                findSendSpuriousLostPackets = re.findall(r"SendSpuriousLostPackets=(\d+)", line)
                
                if re.findall(r"Forgetting", line):
                    Forgetting += 1
                if re.findall(r"Lost: RACK", line):
                    contador_Rack += 1
                if re.findall(r"Lost: FACK", line):
                    contador_Fack += 1
                if re.findall(r"Lost: (\d+)", line):
                    contLostPackets += 1
                if findSendTotalPackets:
                    SendTotalPackets = int(findSendTotalPackets[0]) 
                if findSendSuspectedLostPackets:
                    SendSuspectedLostPackets = int(findSendSuspectedLostPackets[0])
                if findSendSpuriousLostPackets:
                    SendSpuriousLostPackets = int(findSendSpuriousLostPackets[0])

        # Calcular as métricas
        Total_Losses = SendSuspectedLostPackets - SendSpuriousLostPackets
        Loss_Ratio_RACK_FACK = (contador_Fack + contador_Rack) / int(SendTotalPackets) * 100
        RelacaoLost = contLostPackets / int(SendTotalPackets) * 100
        Loss_Ratio_RACK_FACK_FORGETTING = Forgetting / int(SendTotalPackets)

        # Extrair parâmetros do nome do arquivo
        params = file_name.split('-')
        if len(params) >= 8:
            loss = params[2]
            delay = params[3]
            number_of_packets = params[4]
            msg_interval = params[5]
            qos = params[6]
            x = params[7].split('.')[0]  # Remove a extensão do arquivo

            # Adiciona os dados à lista
            results.append([
                loss, delay, number_of_packets, msg_interval, qos, x,
                SendTotalPackets, SendSuspectedLostPackets, SendSpuriousLostPackets,
                Total_Losses, str(contador_Rack), str(contador_Fack),
                str(Loss_Ratio_RACK_FACK), str(Forgetting), str(Loss_Ratio_RACK_FACK_FORGETTING),
                str(contLostPackets), str(RelacaoLost)
            ])
        else:
            pass
    except FileNotFoundError:
        pass
    
    return results


def write_to_csv(data, output_file):
    header = [
        'Loss', 'Delay', 'Number of Msg', 'Message Interval', 'QoS', 'Run_X', 
        'SendTotalPackets', 'SendSuspectedLostPackets', 'SendSpuriousLostPackets', 
        'Total_Losses', 'Lost_RACK', 'Lost_FACK', 'Loss_Ratio_RACK_FACK', 
        'FORGETTING', 'Loss_Ratio_RACK_FACK_FORGETTING', 'All_System_Losses', 
        'Relação ASL/T', 'Totalbytessent', 'TotalUDPsendAPI'
    ]
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)


def process_logs_in_directory(directory, output_file):
    all_results = []

    # Itera sobre todos os arquivos no diretório
    for filename in os.listdir(directory):
        resultadofinal = []
        if filename.startswith('log_msquic'):  # Verifica se é um arquivo de log
            log_file_path = os.path.join(directory, filename)
            resultado_log_msquic = extract_log_msquic(log_file_path)
            tipo_test = filename.replace("log_msquic-", "")
            for filename in os.listdir(directory):
                if filename.startswith('log_tracer') and filename.endswith(tipo_test):
                    log_trace_path = os.path.join(directory, filename)
                    resultado_log_trace = extract_log_trace(log_trace_path)
                    # Concatenar os resultados dos logs
                    resultadofinal = resultado_log_msquic + resultado_log_trace
                    resultado_final = [item for sublist in resultadofinal for item in sublist]
                    all_results.append(resultado_final)
    write_to_csv(all_results, output_file)
    pass


if __name__ == "__main__":
    if len(sys.argv) != 3:
        pass
        sys.exit(1)

    directory = sys.argv[1]
    output_file = sys.argv[2]
    process_logs_in_directory(directory, output_file)
