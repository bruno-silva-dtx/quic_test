#!/usr/bin/env python
import getopt
import socket
import sys
import dtls
import ssl
from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri

__author__ = 'Giacomo Tanganelli'

client = None


def usage():  # pragma: no cover
    print("Command:\tcoapclient.py -o -p [-P]")
    print("Options:")
    print("\t-s, uses DTLS to make the requests")
    print("\t-o, --operation=\tGET|PUT|POST|DELETE|DISCOVER|OBSERVE")
    print("\t-p, --path=\t\t\tPath of the request")
    print("\t-P, --payload=\t\tPayload of the request")
    print("\t-f, --payload-file=\t\tFile with payload of the request")


def client_callback(response):
    print("Callback")


def client_callback_observe(response):  # pragma: no cover
    global client
    print("Callback_observe")
    check = True
    while check:
        chosen = eval(input("Stop observing? [y/N]: "))
        if chosen != "" and not (chosen == "n" or chosen == "N" or chosen == "y" or chosen == "Y"):
            print("Unrecognized choose.")
            continue
        elif chosen == "y" or chosen == "Y":
            while True:
                rst = eval(input("Send RST message? [Y/n]: "))
                if rst != "" and not (rst == "n" or rst == "N" or rst == "y" or rst == "Y"):
                    print("Unrecognized choose.")
                    continue
                elif rst == "" or rst == "y" or rst == "Y":
                    client.cancel_observing(response, True)
                else:
                    client.cancel_observing(response, False)
                check = False
                break
        else:
            break


def main():  # pragma: no cover
    global client
    op = None
    path = None
    payload = None
    secure = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:p:P:f:s:", ["help", "operation=", "path=", "payload=",
                                                               "payload_file=", "secure"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-o", "--operation"):
            op = arg
        elif opt in ("-p", "--path"):
            path = arg
        elif opt in ("-P", "--payload"):
            payload = arg
        elif opt in ("-f", "--payload-file"):
            with open(arg, 'r') as f:
                payload = f.read()
        elif opt in ("-s", "--secure"):
            secure = True
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            usage()
            sys.exit(2)

    if op is None:
        print("Operation must be specified")
        usage()
        sys.exit(2)

    if path is None:
        print("Path must be specified")
        usage()
        sys.exit(2)

    if not path.startswith("coap://"):
        print("Path must be conform to coap://host[:port]/path")
        usage()
        sys.exit(2)

    host, port, path = parse_uri(path)
    try:
        tmp = socket.gethostbyname(host)
        host = tmp
    except socket.gaierror:
        pass

    sock = None
    if secure:
        dtls.do_patch()
        sock = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        sock.connect((host, port))
    client = HelperClient(server=(host, port), sock=sock)
    if op == "GET":
        if path is None:
            print("Path cannot be empty for a GET request")
            usage()
            sys.exit(2)
        response = client.get(path)
        print(response.pretty_print())
        client.stop()
    elif op == "OBSERVE":
        if path is None:
            print("Path cannot be empty for a GET request")
            usage()
            sys.exit(2)
        client.observe(path, client_callback_observe)
        
    elif op == "DELETE":
        if path is None:
            print("Path cannot be empty for a DELETE request")
            usage()
            sys.exit(2)
        response = client.delete(path)
        print(response.pretty_print())
        client.stop()
    elif op == "POST":
        if path is None:
            print("Path cannot be empty for a POST request")
            usage()
            sys.exit(2)
        if payload is None:
            print("Payload cannot be empty for a POST request")
            usage()
            sys.exit(2)
        response = client.post(path, payload)
        print(response.pretty_print())
        client.stop()
    elif op == "PUT":
        if path is None:
            print("Path cannot be empty for a PUT request")
            usage()
            sys.exit(2)
        if payload is None:
            print("Payload cannot be empty for a PUT request")
            usage()
            sys.exit(2)
        response = client.put(path, payload)
        print("path: ", path)
        print("payload: ", payload)
        try:
            print(response.pretty_print())
        except Exception as e:
            print("Request was not successful. ", e)
        client.stop()
    elif op == "DISCOVER":
        response = client.discover()
        print(response.pretty_print())
        client.stop()
    else:
        print("Operation not recognized")
        usage()
        sys.exit(2)


if __name__ == '__main__':  # pragma: no cover
    main()
