FROM ubuntu:22.04

# Dependencias necessárias para compilar o código
RUN apt-get update && \
    apt-get install -y \
    cmake \
    sudo \
    g++ \
    dialog \
    locales \
    man-db \
    manpages \
    less \
    libnng-dev \
    libssl-dev \
    build-essential \
    libpthread-stubs0-dev \
    libc6-dev \
    libc-dev \
    libatomic1 \
    gnupg2 \
    wget \
    curl \
    git \
    openssl \
    apt-transport-https \
    software-properties-common && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get install sudo -y && \
    apt-get full-upgrade -y && \
    apt-get autoremove -y && \
    apt-get install -y \
    libssl-dev \
    libnng-dev 

# Instale o dotnet
RUN apt-get update && \
    apt-get install -y wget && \
    wget https://dot.net/v1/dotnet-install.sh && \
    bash dotnet-install.sh --channel 7.0 --install-dir /usr/share/dotnet && \
    ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet

# Instale o powershell
RUN wget -q https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update && \
    add-apt-repository universe && \
    apt-get install -y powershell

# Instale de lttng
 RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:lttng/stable-2.13 && \
    apt-get update && \
    apt-get install -y liblttng-ust-dev lttng-tools


# Clone the NanoSDK folder to the container
RUN git clone https://github.com/emqx/NanoSDK.git /root/NanoSDK && \
cd /root/NanoSDK && \
git submodule update --init --recursive


# Build the clog2text e o msquic
RUN cd /root/NanoSDK/extern/msquic && \
    git submodule update --init submodules/clog && \
    dotnet build submodules/clog/src/clog2text/clog2text_lttng/ -c Release

# Contruir o msquic
RUN cd /root/NanoSDK/extern/msquic && \
    mkdir build && \
    cd build && \
    cmake  .. -DQUIC_ENABLE_LOGGING=ON  -DQUIC_LOGGING_TYPE="lttng" -DCMAKE_BUILD_TYPE=Debug && \
    make && \
    make install 

# Contruir e instalar o nng
RUN git clone https://github.com/nanomsg/nng.git && \
    cd nng && \
    mkdir build && cd build && \
    cmake .. && \
    make && \
    make install

# Contruir e instalar o NaonoSDK
RUN cd /root/NanoSDK && \
    mkdir build && \
    cd build && \
    cmake ..  -DBUILD_SHARED_LIBS=OFF -DNNG_ENABLE_QUIC=ON -DCMAKE_BUILD_TYPE=Debug -DDEBUG=1 && \
    make && \
    make install

# Copiar e contruir o quic_client
COPY quic_mqtt /root/quic_mqtt 

RUN cd /root/quic_mqtt && \
    mkdir build && \
    cd build && \
    cmake ..  && \
    make
    

