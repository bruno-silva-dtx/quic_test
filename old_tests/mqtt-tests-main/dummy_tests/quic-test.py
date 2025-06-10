import asyncio as asc
import aioquic.asyncio
from aioquic.quic.configuration import QuicConfiguration
import ssl
import argparse
import sys

class Server:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = int(port)
        self.config = QuicConfiguration(
            is_client=False,
            verify_mode=ssl.CERT_NONE
        )
        self.quic_server = None
        self.loop = asc.get_event_loop()

    def start(self):
        self.quic_server = aioquic.asyncio.serve(
                host=self.addr,
                port=self.port,
                configuration=self.config,
                stream_handler=self.run
            )
        self.loop.run_forever()
    
    def run(self, reader, writer):
        self.currentstreamtask = self.loop.create_task(self._currentstreamhandler(reader, writer))
    
    async def _currentstreamhandler(self, reader, writer):
        while True:
            data = await reader.read(1024)
            if not data:
                break
            writer.write(data)
            await writer.drain()
        self.quic_server.close()
        


class Client:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = int(port)

        self.config = QuicConfiguration(
            is_client = True,
            verify_mode = ssl.CERT_NONE
            )

    def start(self):
        loop = asc.get_event_loop()
        loop.run_until_complete(self.run())

    async def run(self):
        async with aioquic.asyncio.connect(host=self.addr, port=self.port, configuration=self.config) as client:
            client.wait_connected()
            reader, writer = await client.create_stream()
            writer.write(b'Hello World!\n')
            client.transmit()
            data = await reader.read(1024)
            print(data)
            client.close()
            await client.wait_closed()



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
