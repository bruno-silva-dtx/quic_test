```mermaid
sequenceDiagram
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0x2851 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0x2852 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 2-0x2853 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 3-0x2854 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 4-0x2855 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 5-0x2856 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 6-0x2857 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 4-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 6-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 9-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 13-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 14-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0xaecf (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0xaed0 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 2-0xaed1 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 4-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 6-0x0000 (Entregue)
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
