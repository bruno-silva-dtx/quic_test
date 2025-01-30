
# Como funciona a Detecção de Perda com FACK

Esse algoritmo é baseado no número de pacotes. Ele considera um pacote como perdido se:

  -  Ele foi enviado antes de um pacote que já foi confirmado;
  -  E foi enviado mais do que um certo número de pacotes atrás (QUIC_PACKET_REORDER_THRESHOLD).



`` [C][TX][104] Lost: FACK 14 packets ``

`` [C][TX][104] Lost: FACK 15 packets ``

`` [C][TX][104] Lost: FACK 16 packets ``

# Como funciona a Detecção de Perda com RACK


**RACK (Recent Acknowledgment)** 

Esse algoritmo é baseado no tempo. Ele assume que um pacote foi perdido se:

-  Ele foi enviado antes de um pacote que já foi confirmado (ACK recebido);
-  E ele foi enviado há mais tempo que o limiar de reordenação temporal (QUIC_TIME_REORDER_THRESHOLD).

`` . ..  `` 


**RACK Timer (Timer de RACK)** 

Este temporizador é ativado quando há pacotes em trânsito e pelo menos um pacote posterior já foi confirmado.
    Sua função é acionar o algoritmo RACK, permitindo detectar perda baseada no tempo.
    Enquanto o temporizador de RACK está ativo, o temporizador de sondagem (Probe Timer) fica inativo, para evitar redundância.


**Probe Timer (Timer de Sondagem)**

    O objetivo deste temporizador é complementar o RACK e garantir que pacotes perdidos sejam identificados em todos os cenários.
    Ele cobre casos em que, por exemplo, o último pacote enviado é perdido, e o RACK não consegue identificá-lo como perdido (porque depende de confirmações de pacotes posteriores).
    O temporizador de sondagem é ativado quando o temporizador de RACK não está ativo e há pacotes em trânsito. Ele é baseado no RTT (tempo de ida e volta) e dobra o intervalo a cada disparo consecutivo.
    Quando este temporizador dispara, dois pacotes de sondagem são enviados, para tentar forçar uma resposta do receptor e identificar qualquer pacote perdido.


As perdas detetados pelo Quic:


´´´


typedef enum QUIC_TRACE_PACKET_LOSS_REASON {
    QUIC_TRACE_PACKET_LOSS_RACK, 
    QUIC_TRACE_PACKET_LOSS_FACK,
    QUIC_TRACE_PACKET_LOSS_PROBE
} QUIC_TRACE_PACKET_LOSS_REASON;

´´´



//
// Different possible packet key types.
//
typedef enum QUIC_PACKET_KEY_TYPE {

    QUIC_PACKET_KEY_INITIAL,
    QUIC_PACKET_KEY_0_RTT,
    QUIC_PACKET_KEY_HANDSHAKE,
    QUIC_PACKET_KEY_1_RTT,
    QUIC_PACKET_KEY_1_RTT_OLD,
    QUIC_PACKET_KEY_1_RTT_NEW,

    QUIC_PACKET_KEY_COUNT

} QUIC_PACKET_KEY_TYPE;







