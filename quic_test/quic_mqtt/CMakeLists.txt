cmake_minimum_required(VERSION 3.13)

project(quic_client)

if (BUILD_DEMO)
else ()
# Call this from your own project's makefile.
  find_package(nng CONFIG REQUIRED)
endif (BUILD_DEMO)

find_package(Threads)
find_package(msquic)
find_package(OpenSSL)

# Adiciona o diretório de inclusão
# include_directories(/home/dtx/Desktop/NanoSDK/include)
include_directories(NanoSDK/include)
if (DEBUG)
  SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -g")
  if (ASAN)
    SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=address")
  endif (ASAN)
  if (TSAN)
    SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=thread")
  endif (TSAN)
endif (DEBUG)

add_executable(quic_client quic_client.c)

if(OPENSSL_FOUND)
    include_directories(${OPENSSL_INCLUDE_DIRS})
    target_link_libraries(quic_client OpenSSL::Crypto OpenSSL::SSL)
endif()

target_link_libraries(quic_client nng::nng msquic pthread)
target_compile_definitions(quic_client PRIVATE NNG_ELIDE_DEPRECATED)

if (NNG_ENABLE_SQLITE)
    add_definitions(-DNNG_SUPP_SQLITE)
    target_link_libraries(quic_client dl)
endif (NNG_ENABLE_SQLITE)
