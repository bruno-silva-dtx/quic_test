```mermaid
sequenceDiagram
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0xe6ba (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0xe6bb (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 2-0xe6bc (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 3-0xe6bd (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 4-0xe6be (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 5-0xe6bf (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 4-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 6-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 9-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 10-0x0000 (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 14-0x0000 (Entregue)
```
```mermaid
pie
  "Pacotes Enviados EMQX -> Cliente" : 6
  "Pacotes Enviados Cliente -> EMQX" : 6
  "Pacotes Perdidos EMQX -> Cliente" : 0
  "Pacotes Perdidos Cliente -> EMQX" : 0
```
##### Total of packets: 12
##### Total of packets EMQX: 12
##### Total of packets Cliente: 12
##### Total of packets sucess EMQX -> Cliente: 6
##### Total of packets sucess Cliente -> EMQX: 6
##### Total of packets lost EMQX -> Cliente: 0
##### Total of packets lost Cliente -> EMQX: 0
