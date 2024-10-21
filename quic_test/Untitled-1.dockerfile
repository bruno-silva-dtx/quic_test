 
      echo "Correr os scrips do msquic"
      docker exec quic_test bash -c '
         cd /root/NanoSDK/extern/msquic && \
         # Conceder permissão de execução aos scripts necessários \
         chmod +x scripts/build.ps1 && \
         chmod +x scripts/prepare-machine.ps1 && \
         # Atualizar e instalar o ambiente \
         apt-get update && \
         apt-get install lttng-tools lttng-modules-dkms -y && \
         pwsh ./scripts/build.ps1 -Config Debug && \
         # pwsh ./scripts/prepare-machine.ps1 -ForTest && \
         sudo apt-add-repository ppa:lttng/stable-2.13 && \
         sudo apt-get update && \
         sudo apt-get install -y lttng-tools 
      '


            
     echo "Correr o make do msquic"
     docker exec quic_test bash -c '
        rm -r build  && \
        mkdir build && cd build  && \
        cmake -DNNG_LOGGING=ON .. && \
        make  && \
        make install 
     '