#!/usr/bin/env python
import os
import sys
import ssl
import argparse
import datetime
import dtls
import socket
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from cryptography.hazmat.backends import default_backend  
from cryptography.hazmat.primitives import serialization  
from cryptography.hazmat.primitives.asymmetric import rsa 
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

class TestResource(Resource):
    def __init__(self, name="TestResource", coap_server=None):
        super(TestResource, self).__init__(name, coap_server, visible=True,
                                           observable=True, allow_children=True)
        self.payload = "Test Resource"

    def render_POST(self, request):
        print(f"Received POST with payload: {request.payload}")
        return self

class CoAPServer(CoAP):
    def __init__(self, host, port, multicast=False, secure=False):
        self.sock = None
        if secure:
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
            dtls.do_patch()
            self.sock = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), server_side=True, certfile='./cert.pem', keyfile='./private_key.key')
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((host, port))
        CoAP.__init__(self, (host, port), multicast, sock=self.sock)
        # Adicione seus recursos existentes
        self.add_resource('basic/', TestResource())
        # Adicione mais recursos conforme necessário
        
        # Adicione o recurso de teste<
        self.add_resource('test/', TestResource())

        print(self.root.dump())

def main():
    # Criar analisador de argumentos
    parser = argparse.ArgumentParser(description='CoAP Server')
    parser.add_argument('-i', '--ip', default='127.0.0.1', help='IP address of the server')
    parser.add_argument('-p', '--port', type=int, default=5683, help='Port number')
    parser.add_argument('-m', '--multicast', action='store_true', help='Enable multicast')
    parser.add_argument('-s', '--secure', action='store_true', help='Enable DTLS (secure mode)')

    # Análise dos argumentos
    args = parser.parse_args()
    
    # Inicialização do servidor CoAP
    server = CoAPServer(args.ip, args.port, multicast=args.multicast, secure=args.secure)
    print(f"Starting CoAP server on {args.ip}:{args.port}, secure={args.secure}")
    try:
        server.listen(10)
    except KeyboardInterrupt:
        print("Server Shutdown")
        server.close()
        print("Exiting...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)