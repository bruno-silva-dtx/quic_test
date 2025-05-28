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
import websockets
import asyncio

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
    
    async def start(self):
        async with websockets.serve(self.handler, self.addr, self.port, ssl=self.context):
            await asyncio.Future()  # run forever

    async def handler(self, websocket):
            message = await websocket.recv()
            print(message)
            await websocket.send(message)
        

class Client:
    def __init__(self, addr, port) -> None:
        self.addr = addr
        self.port = int(port)
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def start(self):
        async with websockets.connect('wss://%s:%s' %(self.addr, self.port), ssl=self.ssl_context) as websocket:
            await websocket.send("Hellow World!")
            response = await websocket.recv()
            print(response)
            await websocket.close()


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
                asyncio.run(server.start())
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
                asyncio.run(client.start())
            else:
                print('Server address not given')
        else:
            print('Server port not given')
    else:
        print('Server or client mode not given')

    # exit program
    sys.exit(0)

