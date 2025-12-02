import socket
import threading
import sys
from gerenciadorConexao import ConnectionHandler
from logs import MetricsLogger

def main():
    """
    Função principal para iniciar o proxy TCP.
    
    Uso: python Proxy.py <PROXY_IP> <PROXY_PORT> <REMOTE_IP> <REMOTE_PORT> <POLICY_MODE>
    Exemplo: python Proxy.py 0.0.0.0 8080 127.0.0.1 8000 pacing
    POLICY_MODE: 'none', 'pacing', 'delayed_ack'
    """
    if len(sys.argv) != 6:
        print(f"Uso: {sys.argv[0]} <PROXY_IP> <PROXY_PORT> <REMOTE_IP> <REMOTE_PORT> <POLICY_MODE>")
        print("POLICY_MODE: 'none', 'pacing', 'delayed_ack'")
        sys.exit(1)

    proxy_host = sys.argv[1]
    proxy_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    policy_mode = sys.argv[5]
    
    # Inicializa o logger
    logger = MetricsLogger(filename=f"log_proxy_{policy_mode}.csv")
    
    # Cria o socket do proxy
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((proxy_host, proxy_port))
        server_socket.listen(5)
        
        print(f"TCP Proxy escutando em {proxy_host}:{proxy_port}")
        print(f"Encaminhando para {remote_host}:{remote_port}")
        print(f"Política de Otimização Ativa: **{policy_mode.upper()}**")
        
    except Exception as e:
        print(f"Não foi possível iniciar o servidor proxy: {e}")
        sys.exit(1)
        
    connection_counter = 0
    try:
        while True:
            # Espera por novas conexões de clientes
            client_socket, client_addr = server_socket.accept()
            connection_counter += 1
            print(f"\n--- Nova Conexão ---")
            print(f"Recebida conexão de: {client_addr[0]}:{client_addr[1]}")
            
            # Cria um novo thread para gerenciar a conexão
            handler = ConnectionHandler(
                client_socket, client_addr, remote_host, remote_port, 
                connection_counter, logger, policy_mode
            )
            handler.start()
            
    except KeyboardInterrupt:
        print("\nProxy desligado pelo usuário.")
    except Exception as e:
        print(f"Erro inesperado no loop principal: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()