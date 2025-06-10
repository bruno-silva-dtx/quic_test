import argparse
import ssl
import datetime
import time
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from coapthon.client.helperclient import HelperClient

def create_dtls_context():
    # Geração de chave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,  # Reduzido para 2048 para exemplo
        backend=default_backend()
    )

    # Criação de um certificado autoassinado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "PT"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Braga"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Guimaraes"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DTx CoLab"),
        x509.NameAttribute(NameOID.COMMON_NAME, "dtx-colab.pt"),
    ])
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # Validade de 10 dias
        datetime.datetime.utcnow() + datetime.timedelta(days=10)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName("localhost")]),
        critical=False
    ).sign(private_key, hashes.SHA256(), default_backend())

    # Escrita do certificado e chave privada nos arquivos
    with open("client_certificate.pem", "wb") as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))

    with open("client_key.pem", "wb") as key_file:
        key_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Configuração do contexto SSL para DTLS
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_cert_chain(certfile="client_certificate.pem", keyfile="client_key.pem")
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    return context

def send_coap_request(host, port, path, security_context, n_messages, msg_size, msg_interval):
    print(f"Starting to send {n_messages} messages...")
    client = HelperClient(server=(host, port))
    for i in range(n_messages):
        payload = b'0' * msg_size  # Criar payload baseado no msg_size fornecido
        print(f"Sending message {i+1}/{n_messages} with size {msg_size}")
        response = client.post(path, payload)
        print("Sent:", payload)
        print("Response:", response.pretty_print())
        print("Msg interval:", msg_interval)
        time.sleep(int(msg_interval))  # Esperar msg_interval segundos antes de enviar a próxima mensagem
    print(f"Finished sending {n_messages} messages.")
    client.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CoAP DTLS client example')
    parser.add_argument('-b', '--host',  default='127.0.0.1',help='Host address', required=True)
    parser.add_argument('-p', '--port', type=int, help='Port number', default=5683)
    parser.add_argument('-t', '--transport', choices=['tcp', 'dtls'], default='tcp', help='Transport protocol (tcp or dtls)')
    parser.add_argument('-n', '--n_messages',type=int, help='The number of messages published')
    parser.add_argument('-s', '--msg_size', type=int, help='The message size in bytes')
    parser.add_argument('-i', '--msg_interval', help='The interval between messages in seconds')
    
    args = parser.parse_args()

    if args.transport == 'dtls':
        dtls_context = create_dtls_context()
        send_coap_request(args.host, args.port, '127.0.0.1', dtls_context, args.n_messages, args.msg_size, args.msg_interval)
    else:
        send_coap_request(args.host, args.port, '127.0.0.1', None, args.n_messages, args.msg_size, args.msg_interval)