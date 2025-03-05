```mermaid
sequenceDiagram
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 0-0xcccb (Entregue)
 EMQX--xCliente: QUIC Packet 172.18.0.2->172.18.0.3: 0-0x0000 (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 1-0xcccc (Perda)
 EMQX--xCliente: QUIC Packet 172.18.0.2->172.18.0.3: 4-0x0000 (Perda)
 Cliente--xEMQX: QUIC Packet 172.18.0.3->172.18.0.2: 2-0xcccd (Perda)
 EMQX->>Cliente: QUIC Packet 172.18.0.2->172.18.0.3: 6-0x0000 (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 3-0xccce (Entregue)
 Cliente->>EMQX: QUIC Packet 172.18.0.3->172.18.0.2: 5-0xcccf (Entregue)
```
```mermaid
pie
  "Pacotes Enviados EMQX -> Cliente" : 1
  "Pacotes Enviados Cliente -> EMQX" : 3
  "Pacotes Perdidos EMQX -> Cliente" : 2
  "Pacotes Perdidos Cliente -> EMQX" : 2
```
##### Total of packets: 8
##### Total of packets EMQX: 6
##### Total of packets Cliente: 6
##### Total of packets sucess EMQX -> Cliente: 1
##### Total of packets sucess Cliente -> EMQX: 3
##### Total of packets lost EMQX -> Cliente: 2
##### Total of packets lost Cliente -> EMQX: 2
