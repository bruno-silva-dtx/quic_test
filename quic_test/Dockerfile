FROM ubuntu:22.04

# Dependencias necessárias para compilar o código
RUN apt-get update && \
    apt-get install -y \
    cmake \
    ninja-build \
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
    lttng-modules-dkms \
    babeltrace2 \
    libssl-dev \
    libnng-dev \
    pkg-config \
    git \
    curl \
    wget \
    python3-pip \
    pkg-config \
    autoconf \
    automake \
    libtool \
    libbabeltrace-dev \
    liburcu-dev \
    dotnet-runtime-6.0 \
    dotnet-sdk-6.0 \
    dotnet-host



# Instale o powershell
RUN wget -q https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update && \
    add-apt-repository universe && \
    apt-get install -y powershell

# Instale de lttng
RUN  apt-add-repository ppa:lttng/stable-2.13 && \
    apt-get update && \
    apt-get install -y liblttng-ust liblttng-ust-dev lttng-tools 


# Clone the NanoSDK folder to the container
RUN git clone https://github.com/emqx/NanoSDK.git /root/NanoSDK && \
cd /root/NanoSDK && \
git submodule update --init --recursive


# Build the clog2text e o msquic
RUN cd /root/NanoSDK/extern/msquic && \
    git submodule update --init submodules/clog && \
    dotnet build submodules/clog/src/clog2text/clog2text_lttng/ -c Release

# Contruir o msquic
RUN cd /NanoSDK/extern/msquic && \
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
    cmake ..  -DBUILD_SHARED_LIBS=OFF -DNNG_ENABLE_QUIC=ON -DCMAKE_BUILD_TYPE=Debug  && \
    make && \
    make install

# Copiar e contruir o quic_client
COPY quic_client /root/quic_client 

RUN cd /root/quic_client && \
    mkdir build && \
    cd build && \
    cmake .. -DDEBUG=1 && \
    make


