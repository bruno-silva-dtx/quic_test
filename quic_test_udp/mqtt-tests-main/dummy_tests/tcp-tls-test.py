import sys
import argparse
import socket
import ssl
import datetime
from cryptography.hazmat.backends import default_backend  
from cryptography.hazmat.primitives import serialization  
from cryptography.hazmat.primitives.asymmetric import rsa  
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from time import sleep

class Server:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = int(port)
        self.private_key = rsa.generate_private_key(  
            public_exponent=65537,  
            key_size=4096,  
            backend=default_backend()  
        )

        subject = issuer = x509.Name([ 
            x509.NameAttribute(NameOID.COUNTRY_NAME, "PT"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Braga"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Guimaraes"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DTx CoLab"),
            x509.NameAttribute(NameOID.COMMON_NAME, "dtx-colab.pt"),
        ])
        cert = x509.CertificateBuilder().subject_name(
            subject).issuer_name(
            issuer).public_key(
            self.private_key.public_key()).serial_number(
            x509.random_serial_number()).not_valid_before(
            datetime.datetime.now(datetime.timezone.utc)).not_valid_after(
            # Our certificate will be valid for 10 days
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10)
            ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
            # Sign our certificate with our private key
            ).sign(self.private_key, hashes.SHA256())

        # Write our certificate out to disk.

        with open('./cert.pem', mode='w+b') as cert_file: 
            cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
            cert_file.close()           
        
        with open('./private_key.key', mode='w+b') as key_file:
            key_file.write(
                self.private_key.private_bytes(   
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
            key_file.close()

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain('./cert.pem', './private_key.key')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.sock.bind((self.addr, self.port))    
        self.sock.listen(1)
        with self.context.wrap_socket(self.sock, server_side=True) as ssock:
            conn, addr = ssock.accept()
            print('Connected by', addr)
            while True:
                try:
                    data = conn.recv(1024)
                    if not data: break
                    print(data.decode('utf-8'))
                    conn.sendall(data)
                except ConnectionResetError:
                    print('Connection reset by peer')
                    break

        conn.close()
        

class Client:
    def __init__(self, addr, port) -> None:
        self.addr = addr
        self.port = int(port)
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = False
    
    def start(self):
        with socket.create_connection((self.addr, self.port)) as sock:
            with self.context.wrap_socket(sock, server_hostname=str(self.addr)+':'+str(self.port)) as ssock:
                print(ssock.version())
                ssock.sendall(b'Hello, world')
                data = ssock.recv(1024)
                print('Received', repr(data))
                ssock.close()


if __name__ == '__main__':
    # create argument parser
    parser = argparse.ArgumentParser(description='TCP TLS server and client test')
    parser.add_argument('-s', '--server', action='store_true', help='Running server mode', required=False)
    parser.add_argument('-c', '--client', action='store_true', help='Running client mode', required=False)
    parser.add_argument('-p', '--port', help='Server port', required=True)
    parser.add_argument('-a', '--addr', help='Server address', required=True)

    # parse arguments
    args = parser.parse_args()

    # check if server mode
    if args.server:
        # check if port is given
        if args.port:
            # check if address is given
            if args.addr:
                # create server
                server = Server(args.addr, args.port)
                # start server
                server.start()
            else:
                print('Server address not given')
        else:
            print('Server port not given')

    # check if client mode
    elif args.client:
        # check if port is given
        if args.port:
            # check if address is given
            if args.addr:
                # create client
                client = Client(args.addr, args.port)
                # start client
                client.start()
            else:
                print('Server address not given')
        else:
            print('Server port not given')
    else:
        print('Server or client mode not given')

    # exit program
    sys.exit(0)

