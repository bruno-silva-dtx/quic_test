#!/usr/bin/env python

import getopt
import sys
import dtls
import ssl
import datetime
import socket
from cryptography.hazmat.backends import default_backend  
from cryptography.hazmat.primitives import serialization  
from cryptography.hazmat.primitives.asymmetric import rsa  
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from coapthon.server.coap import CoAP
from exampleresources import BasicResource, Long, Separate, Storage, Big, voidResource, XMLResource, ETAGResource, \
    Child, \
    MultipleEncodingResource, AdvancedResource, AdvancedResourceSeparate

import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

__author__ = 'Giacomo Tanganelli and Vinicius Ferreira'


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
        self.add_resource('basic/', BasicResource())
        self.add_resource('storage/', Storage())
        self.add_resource('separate/', Separate())
        self.add_resource('long/', Long())
        self.add_resource('big/', Big())
        self.add_resource('void/', voidResource())
        self.add_resource('xml/', XMLResource())
        self.add_resource('encoding/', MultipleEncodingResource())
        self.add_resource('etag/', ETAGResource())
        self.add_resource('child/', Child())
        self.add_resource('advanced/', AdvancedResource())
        self.add_resource('advancedSeparate/', AdvancedResourceSeparate())
        print(self.root.dump())







def usage():  # pragma: no cover
    print("coapserver.py -i <ip address> -p <port>")


def main(argv):  # pragma: no cover
    ip = "127.0.0.1"
    port = 5683
    multicast = False
    secure = False
    try:
        opts, args = getopt.getopt(argv, "hi:p:m:s", ["ip=", "port=", "multicast", "secure"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-m", "--multicast"):
            multicast = True
        elif opt in ("-s", "--secure"):
            secure = True

    server = CoAPServer(ip, port, multicast, secure)
    try:
        server.listen(10)
    except KeyboardInterrupt:
        print("Server Shutdown")
        server.close()
        print("Exiting...")


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
