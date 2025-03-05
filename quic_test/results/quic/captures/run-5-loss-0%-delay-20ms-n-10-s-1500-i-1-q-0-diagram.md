```mermaid
sequenceDiagram
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0x1f9c (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0x1f9d (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 2-0x1f9e (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 3-0x1f9f (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 4-0x1fa0 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 5-0x1fa1 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 4-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 6-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 9-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 13-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 14-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0x1c02 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0x1c03 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 2-0x1c04 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 4-0x0000 (Entregue)
```
```mermaid
pie
  "Pacotes Enviados EMQX -> Cliente" : 8
  "Pacotes Enviados Cliente -> EMQX" : 9
  "Pacotes Perdidos EMQX -> Cliente" : 0
  "Pacotes Perdidos Cliente -> EMQX" : 0
```
##### Total of packets: 17
##### Total of packets EMQX: 17
##### Total of packets Cliente: 17
##### Total of packets sucess EMQX -> Cliente: 8
##### Total of packets sucess Cliente -> EMQX: 9
##### Total of packets lost EMQX -> Cliente: 0
##### Total of packets lost Cliente -> EMQX: 0
