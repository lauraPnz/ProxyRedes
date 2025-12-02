import socket
import threading
import sys

# Constantes
ECHOMAX = 81
SERVER_HOST = '0.0.0.0' # INADDR_ANY em Python
SERVER_PORT = 8000      # Porta de escuta (REMOTE_PORT do proxy)

def handle_client(client_socket, client_address):
    """Lida com a comunicação de um único cliente (via proxy) e ecoa a mensagem."""
    print(f"[SERVER] Conexão aceita de {client_address[0]}:{client_address[1]}")
    
    # Simula o socket original loc_newsockfd
    loc_newsockfd = client_socket 
    
    try:
        while True:
            # Recebe dados do cliente (via proxy)
            # recv(tamanho_da_memoria)
            linha = loc_newsockfd.recv(ECHOMAX) 
            
            if not linha:
                # Se não há mais dados, a conexão foi fechada pelo cliente
                break

            message = linha.decode('utf-8').strip('\x00') # Decodifica e remove nulos
            print(f"[SERVER] Recebi: '{message}'")

            # Envia a linha de volta (echo)
            # send(endereco_da_memoria, tamanho_da_memoria, flag)
            loc_newsockfd.sendall(linha)
            print(f"[SERVER] Renvia: '{message}'")
            
            # Verifica a condição de saída
            if message.lower() == "exit":
                break

    except Exception as e:
        # Erro de conexão ou socket
        print(f"[SERVER] Erro na conexão com {client_address[0]}:{client_address[1]}: {e}")
    finally:
        # Fechamento do socket (equivale a close(loc_newsockfd))
        print(f"[SERVER] Conexão com {client_address[0]}:{client_address[1]} encerrada.")
        loc_newsockfd.close()

def main_server():
    if len(sys.argv) == 2:
        try:
            global SERVER_PORT
            SERVER_PORT = int(sys.argv[1])
        except ValueError:
            print("Porta inválida.")
            sys.exit(1)
    
    try:
        # Cria o socket (socket(AF_INET, SOCK_STREAM, 0))
        loc_sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        loc_sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind para o endereco local
        # bind(loc_sockfd, estrutura do endereco local, comprimento do endereco)
        loc_sockfd.bind((SERVER_HOST, SERVER_PORT))
        
        # Listen (descritor socket, numeros de conexoes em espera)
        loc_sockfd.listen(5)
        print(f"[*] Servidor TCP escutando em {SERVER_HOST}:{SERVER_PORT}")
        print("> aguardando conexao")

        while True:
            # Accept (devolve um novo socket e o endereco do cliente)
            # loc_newsockfd = accept(...)
            client_sock, client_addr = loc_sockfd.accept()

            # Lida com o cliente em uma nova thread (para aceitar múltiplas conexões)
            client_handler = threading.Thread(target=handle_client, args=(client_sock, client_addr))
            client_handler.start()

    except KeyboardInterrupt:
        print("\nServidor TCP desligado pelo usuário.")
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
    finally:
        # Fechamento do socket original (close(loc_sockfd))
        if 'loc_sockfd' in locals():
            loc_sockfd.close()

if __name__ == '__main__':
    # Uso opcional: python server.py <port>
    main_server()