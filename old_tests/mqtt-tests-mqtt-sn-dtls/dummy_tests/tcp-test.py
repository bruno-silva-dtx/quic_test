import sys
import argparse
import socket
import asyncio

from time import sleep

class Server:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = int(port)
        
    async def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.addr, self.port))    
        self.sock.listen(1)
        loop = asyncio.get_event_loop()
        while True:
            conn, addr = await loop.sock_accept(self.sock)
            print('Connected by', addr)
            asyncio.create_task(self.handle_client(conn))
            await asyncio.Future()


    async def handle_client(self, client):
        loop = asyncio.get_event_loop()        
        data = (await loop.sock_recv(client, 1024)).decode('utf8')
        print(data)
        await loop.sock_sendall(client, data.encode('utf8'))
        
        

class Client:
    def __init__(self, addr, port) -> None:
        self.addr = addr
        self.port = int(port)
    
    async def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.addr, self.port))
        loop = asyncio.get_event_loop()
        await loop.sock_sendall(self.sock, b'Hello World!')
        response = (await loop.sock_recv(self.sock, 1024)).decode('utf8')
        print(response)
        self.sock.close()


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

