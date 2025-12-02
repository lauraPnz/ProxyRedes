import socket
import sys
import time

# Constantes
ECHOMAX = 81

def main_client():
    if len(sys.argv) != 3:
        print(f"Uso: python {sys.argv[0]} <remote_host> <remote_port>")
        sys.exit(1)

    # ESTACAO REMOTA
    rem_hostname = sys.argv[1]
    rem_port = int(sys.argv[2])
    
    # Cria o socket (socket(AF_INET, SOCK_STREAM, 0))
    rem_sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        print(f"> Conectando no servidor '{rem_hostname}:{rem_port}'")

        # Estabelece uma conexao remota (connect(...))
        rem_sockfd.connect((rem_hostname, rem_port))
        print("Conexão estabelecida. Digite 'exit' para sair.")

        while True:
            # Leitura da linha do stdin (fgets e gets)
            linha = input(">> Digite a mensagem: ")
            
            # Codifica a linha para bytes e preenche com nulos até ECHOMAX (similar ao C)
            data_to_send = linha.encode('utf-8')
            # Garante que o buffer tem o tamanho ECHOMAX, preenchendo com nulos
            buffer_send = bytearray(ECHOMAX)
            buffer_send[:len(data_to_send)] = data_to_send
            
            # Envio (send(rem_sockfd, &linha, sizeof(linha), 0))
            rem_sockfd.sendall(buffer_send)

            if linha.lower() == "exit":
                break
                
            # Recebimento (recv(rem_sockfd, &linha, sizeof(linha), 0))
            buffer_recv = rem_sockfd.recv(ECHOMAX)
            
            # Decodifica e limpa a string
            received_message = buffer_recv.decode('utf-8').strip('\x00')
            print(f"Recebi {received_message}")

            # Verifica a condição de saída
            if received_message.lower() == "exit":
                break
                
    except ConnectionRefusedError:
        print(f"\n[ERRO] Conexão recusada em {rem_hostname}:{rem_port}. O proxy está rodando?")
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um erro na conexão: {e}")
    finally:
        # Fechamento do socket (close(rem_sockfd))
        print("Fechando o socket cliente.")
        rem_sockfd.close()

if __name__ == '__main__':
    main_client()