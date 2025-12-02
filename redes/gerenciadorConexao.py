import socket
import threading
import time
import select
from otimiza import OptimizationPolicies
from logs import MetricsLogger
import random

class ConnectionHandler(threading.Thread):
    """
    Gerencia uma única conexão Cliente <-> Proxy <-> Servidor.
    """
    
    def __init__(self, client_socket, client_addr, remote_host, remote_port, 
                 conn_id, logger, policy_mode='none'):
        super().__init__()
        self.client_socket = client_socket
        self.client_addr = client_addr
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.conn_id = conn_id
        self.logger = logger
        self.policy_mode = policy_mode.lower()

        # Configurações de conexão
        self.remote_socket = None
        self.buffer_size = 4096
        self.running = True
        
        # Variáveis de monitoramento (Simuladas/Estimadas)
        self.rtt_min = 0.05  # RTT inicial em segundos (50ms)
        self.rtt_estimated = self.rtt_min
        self.retransmissions = 0
        self.bytes_received = 0
        self.start_time = time.time()
        self.last_log_time = time.time()
        
        # Variáveis de Otimização
        self.last_ack_time = 0
        self.last_send_time = 0
        self.cwnd_simulated = self.buffer_size # Simulação de Janela de Congestionamento

    def run(self):
        """Lógica principal do thread de conexão."""
        try:
            # 1. Estabelecer conexão com o servidor remoto
            self.remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # O proxy pode aplicar um ajuste de buffer aqui (Etapa 3)
            # self.remote_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65535)
            self.remote_socket.connect((self.remote_host, self.remote_port))
            
            print(f"[{self.conn_id}] Conexão estabelecida com {self.remote_host}:{self.remote_port}")
            
            # 2. Loop de encaminhamento de tráfego
            self.forward_traffic()
            
        except ConnectionRefusedError:
            print(f"[{self.conn_id}] Erro: Conexão recusada pelo servidor.")
        except Exception as e:
            print(f"[{self.conn_id}] Erro na conexão: {e}")
        finally:
            self.cleanup()

    def forward_traffic(self):
        """Encaminha o tráfego entre cliente e servidor com monitoramento e políticas."""
        sockets_list = [self.client_socket, self.remote_socket]
        
        while self.running:
            # Uso de select para monitorar múltiplos sockets simultaneamente
            read_sockets, _, _ = select.select(sockets_list, [], [], 1.0) # Timeout 1s

            # 1. Lógica do Cliente -> Servidor (Via Proxy)
            for sock in read_sockets:
                try:
                    # Dados vindos do Cliente
                    if sock == self.client_socket:
                        data = sock.recv(self.buffer_size)
                        if not data:
                            self.running = False # Cliente desconectou
                            break
                        
                        # --- MONITORAMENTO E OTIMIZAÇÃO AQUI (Etapa 2/3) ---
                        
                        # 1.1 Simulação de Pacing (Cliente -> Servidor)
                        if self.policy_mode == 'pacing':
                            delay = OptimizationPolicies.calculate_pacing_delay(
                                target_rate_mbps=1.0, 
                                packet_size_bytes=len(data)
                            )
                            # Se o tempo desde o último envio for muito curto, espera
                            if delay > 0 and (time.time() - self.last_send_time) < delay:
                                time.sleep(delay - (time.time() - self.last_send_time))
                            self.last_send_time = time.time()
                            
                        # 1.2 Encaminhamento (e contagem de bytes)
                        self.remote_socket.sendall(data)
                        self.bytes_received += len(data)

                    # Dados vindos do Servidor (ACKs/Dados)
                    elif sock == self.remote_socket:
                        data = sock.recv(self.buffer_size)
                        if not data:
                            self.running = False # Servidor desconectou
                            break

                        # 2.1 Simulação de Delayed ACK (Servidor -> Cliente)
                        # Assumimos que a resposta do servidor pode ser um ACK ou dados.
                        if self.policy_mode == 'delayed_ack':
                            ack_delay = OptimizationPolicies.delayed_ack_delay(self.rtt_estimated)
                            if time.time() - self.last_ack_time < ack_delay:
                                # Poderia acumular pacotes/ACks aqui antes de enviar...
                                pass 
                            self.last_ack_time = time.time()
                            time.sleep(ack_delay) # Simula o atraso na resposta
                            
                        # 2.2 Encaminhamento
                        self.client_socket.sendall(data)
                        
                except ConnectionResetError:
                    print(f"[{self.conn_id}] Conexão forçada a fechar.")
                    self.running = False
                    break
                except Exception as e:
                    print(f"[{self.conn_id}] Erro durante o encaminhamento: {e}")
                    self.running = False
                    break
                    
            # 3. Log e Visualização Periódica (Etapa 4)
            if time.time() - self.last_log_time >= 1.0: # A cada 1 segundo
                self.collect_and_log_metrics()
                self.last_log_time = time.time()
                
    def collect_and_log_metrics(self):
        """Coleta as métricas estimadas e as registra."""
        duration = time.time() - self.start_time
        if duration < 0.1: # Evita divisão por zero no início
            return

        # --- Métrica RTT (Simulada/Estimada) ---
        # No mundo real, seria medido com timestamps (pcap) ou via tcp_info.
        # Aqui, RTT é ajustado para simular variação de rede.
        # Em um teste real com 'tc', as variações de latência afetariam
        # o tempo de conexão, o que indiretamente afetaria a medição de tempo real.
        self.rtt_estimated += random.uniform(-0.01, 0.01) # Simula um pouco de jitter
        self.rtt_estimated = max(self.rtt_min, self.rtt_estimated) # RTT não pode ser negativo
        rtt_ms = self.rtt_estimated * 1000

        # --- Métrica Throughput (Estimada) ---
        # Throughput total desde o início da conexão.
        throughput_kbps = (self.bytes_received * 8) / duration / 1024 # B * 8 -> bits / s -> kbps
        
        # --- Outras Métricas (Simuladas) ---
        # cwnd e retransmissões são geralmente APIs do OS, aqui são placeholders:
        # A retransmissão pode ser contada se houver timeout (não implementado aqui).
        
        metrics = {
            'rtt_ms': rtt_ms,
            'throughput_kbps': throughput_kbps,
            'retransmissions': self.retransmissions,
            'cwnd_simulated': self.cwnd_simulated,
            'policy_applied': self.policy_mode
        }
        
        self.logger.log_metrics(self.conn_id, self.client_addr, metrics)
        self.logger.print_metrics(self.conn_id, metrics)


    def cleanup(self):
        """Fecha os sockets e limpa os recursos."""
        print(f"[{self.conn_id}] Fechando conexão.")
        if self.remote_socket:
            self.remote_socket.close()
        if self.client_socket:
            self.client_socket.close()