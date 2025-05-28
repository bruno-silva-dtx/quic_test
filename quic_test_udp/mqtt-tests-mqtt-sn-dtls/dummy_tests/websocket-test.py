import sys
import argparse
import socket
import websockets
import asyncio
from time import sleep

class Server:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = int(port)

    async def start(self):
        async with websockets.serve(self.handler, self.addr, self.port):
            await asyncio.Future()  # run forever

    async def handler(self, websocket):
            message = await websocket.recv()
            print(message)
            await websocket.send(message)

class Client:
    def __init__(self, addr, port) -> None:
        self.addr = addr
        self.port = int(port)
    
    async def start(self):
        async with websockets.connect('ws://%s:%s' %(self.addr, self.port)) as websocket:
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

