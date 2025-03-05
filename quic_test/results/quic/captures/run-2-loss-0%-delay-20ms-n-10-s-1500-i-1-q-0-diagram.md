```mermaid
sequenceDiagram
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0xeab0 (Perda)
 EMQX--xCliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0xeab1 (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0x5ec2 (Perda)
 EMQX--xCliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0x5ec3 (Perda)
 EMQX--xCliente: QUIC Packet 172.18.0.2->172.18.0.3: 4-0x0000 (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 2-0x5ec4 (Perda)
 EMQX--xCliente: QUIC Packet 172.18.0.2->172.18.0.3: 6-0x0000 (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 3-0x5ec5 (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0x03fa (Perda)
 EMQX--xCliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0x03fb (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0x7fc0 (Perda)
 EMQX--xCliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0x7fc1 (Perda)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0x2e39 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0x2e3a (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 2-0x2e3b (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 3-0x2e3c (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 4-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 6-0x0000 (Entregue)
```
```mermaid
pie
  "Pacotes Enviados EMQX -> Cliente" : 3
  "Pacotes Enviados Cliente -> EMQX" : 4
  "Pacotes Perdidos EMQX -> Cliente" : 6
  "Pacotes Perdidos Cliente -> EMQX" : 10
```
##### Total of packets: 23
##### Total of packets EMQX: 23
##### Total of packets Cliente: 7
##### Total of packets sucess EMQX -> Cliente: 3
##### Total of packets sucess Cliente -> EMQX: 4
##### Total of packets lost EMQX -> Cliente: 6
##### Total of packets lost Cliente -> EMQX: 10
