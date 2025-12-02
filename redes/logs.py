import csv
import time
import os

class MetricsLogger:
    """
    Gerencia o registro de métricas em um arquivo CSV.
    """
    def __init__(self, filename="metrics_log.csv"):
        self.filename = filename
        self.fieldnames = ['timestamp', 'connection_id', 'client_addr', 'rtt_ms', 
                           'throughput_kbps', 'retransmissions', 'cwnd_simulated', 
                           'policy_applied']
        self.initialize_log()

    def initialize_log(self):
        """Cria o arquivo CSV com o cabeçalho se ele não existir."""
        file_exists = os.path.isfile(self.filename)
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            if not file_exists:
                writer.writeheader()

    def log_metrics(self, connection_id, client_addr, metrics):
        """Registra uma linha de métricas."""
        # Combina métricas com info de conexão e um timestamp
        log_entry = {
            'timestamp': time.time(),
            'connection_id': connection_id,
            'client_addr': f"{client_addr[0]}:{client_addr[1]}",
            **metrics
        }

        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writerow(log_entry)

    def print_metrics(self, connection_id, metrics):
        """Exibe as métricas na interface de monitoramento (texto)."""
        print(f"\n--- Conexão #{connection_id} ---")
        for key, value in metrics.items():
            if 'ms' in key:
                print(f"  {key}: {value:.2f} ms")
            elif 'kbps' in key:
                print(f"  {key}: {value:.2f} kbps")
            else:
                print(f"  {key}: {value}")
        print("---------------------------")