import time
import random

class OptimizationPolicies:
    """
    Implementa as políticas de ajuste dinâmico para a conexão.
    """
    
    # Exemplo 1: Delayed ACK Adaptativo (Simulado)
    @staticmethod
    def delayed_ack_delay(estimated_rtt):
        """
        Calcula um atraso intencional para o ACK, 
        baseado no RTT estimado (em segundos).
        Atraso: RTT/4 ou um valor fixo mínimo, o que for maior.
        """
        # ACK deve ser atrasado para coincidir com o próximo pacote de dados,
        # ou no máximo 500ms (regra TCP). Aqui usamos RTT como base.
        min_delay = 0.05  # Mínimo de 50ms (Exemplo)
        adaptive_delay = estimated_rtt / 4.0
        
        # Simula o atraso na confirmação
        delay = max(min_delay, adaptive_delay)
        return delay

    # Exemplo 2: TCP Pacing (Simulado - Limitação de Taxa)
    @staticmethod
    def calculate_pacing_delay(target_rate_mbps, packet_size_bytes):
        """
        Calcula o atraso necessário entre o envio de pacotes para atingir
        uma taxa de envio (pacing).
        
        target_rate_mbps: Taxa desejada em Mbps
        packet_size_bytes: Tamanho do pacote (ou buffer de envio) em bytes
        
        Retorna o tempo de atraso em segundos.
        """
        if target_rate_mbps <= 0:
            return 0.0

        # Conversão de Mbps para Bytes/seg
        target_rate_bps = target_rate_mbps * 1024 * 1024
        target_rate_Bps = target_rate_bps / 8
        
        # Tempo necessário para enviar 'packet_size_bytes'
        if target_rate_Bps > 0:
            delay = packet_size_bytes / target_rate_Bps
            return delay
        else:
            return 0.0
            
    # Mais políticas podem ser adicionadas aqui...