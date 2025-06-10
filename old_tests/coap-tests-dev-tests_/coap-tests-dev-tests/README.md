# CoAP Tests Repository

This repository contains the code for CoAP tests for BE.Neutral's data protocol assessment. Follow the instructions below to set up and run the IoT protocol.

## Pre requisites

Before you begin, ensure you have the following dependencies installed:

- Docker
- Python 3.8

This is based on CoAPthon3 with a few modifications to enable DTLS. 
To run with DTLS enabled use the flag --secure
PS: The DTLS is still under construction and might present bugs 

## Usage

1. **Start Server**: Run the following command to start the CoAP server:

   ```bash
   python3 CoAPthon3/coapserver.py 
   ```

2. **GET Request**: Run the following command to make a GET request on resource /basic/test (it should start empty, i.e., return NONE):

    ```bash
    python3 CoAPthon3/coapclient.py -o GET -p coap://localhost/basic/test
    ```

3. **POST Request**: Run the following command to make a POST request to create a new resource on /basic/test and use the README.md file as payload:

    ```bash 
    python3 CoAPthon3/coapclient.py -o POST -p coap://localhost/basic/test -f README.md
    ```

4. **DELETE Request**: Run the following command to make a DELETE request and remove the created resource (/basic/test) from the server:

    ```bash 
    python3 CoAPthon3/coapclient.py -o DELETE -p coap://localhost/basic/test
    ```    