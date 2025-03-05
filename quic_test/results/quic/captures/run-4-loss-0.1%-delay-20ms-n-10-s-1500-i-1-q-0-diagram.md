```mermaid
sequenceDiagram
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0xc0fe (Entregue)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0xc0ff (Entregue)
```
```mermaid
pie
  "Pacotes Enviados EMQX -> Cliente" : 1
  "Pacotes Enviados Cliente -> EMQX" : 2
  "Pacotes Perdidos EMQX -> Cliente" : 0
  "Pacotes Perdidos Cliente -> EMQX" : 0
```
##### Total of packets: 3
##### Total of packets EMQX: 3
##### Total of packets Cliente: 3
##### Total of packets sucess EMQX -> Cliente: 1
##### Total of packets sucess Cliente -> EMQX: 2
##### Total of packets lost EMQX -> Cliente: 0
##### Total of packets lost Cliente -> EMQX: 0
