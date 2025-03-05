```mermaid
sequenceDiagram
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0xfef0 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0xfef1 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 2-0xfef2 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 3-0xfef3 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 4-0xfef4 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 5-0xfef5 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 6-0xfef6 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 7-0xfef7 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 9-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 10-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 14-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 15-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 4-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 6-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 7-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0x5873 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0x5874 (Entregue)
```
```mermaid
pie
  "Pacotes Enviados EMQX -> Cliente" : 9
  "Pacotes Enviados Cliente -> EMQX" : 10
  "Pacotes Perdidos EMQX -> Cliente" : 0
  "Pacotes Perdidos Cliente -> EMQX" : 0
```
##### Total of packets: 19
##### Total of packets EMQX: 19
##### Total of packets Cliente: 19
##### Total of packets sucess EMQX -> Cliente: 9
##### Total of packets sucess Cliente -> EMQX: 10
##### Total of packets lost EMQX -> Cliente: 0
##### Total of packets lost Cliente -> EMQX: 0
