import socket
import json
import time
import random

TAM_FRAGMENTO = 3
JANELA = 4
TEMPO_TIMEOUT = 2
SIMULAR_ERRO = True
SIMULAR_PERDA = True

def calcular_checksum(payload):
    return sum(ord(c) for c in payload)

def fragmentar_mensagem(mensagem):
    return [mensagem[i:i+TAM_FRAGMENTO] for i in range(0, len(mensagem), TAM_FRAGMENTO)]

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 9000))

    modo = input("Modo de operação (individual/grupo): ").strip()
    tam_max = int(input("Tamanho máximo do grupo (padrão 6): ") or "6")
    protocolo = {"modo_operacao": modo, "tam_max": tam_max}
    s.sendall((json.dumps(protocolo) + '\n').encode())

    resposta = s.recv(1024).decode()
    print(f"Handshake resposta: {resposta.strip()}")

    mensagem = input("Digite a mensagem para enviar: ").strip()
    pacotes = fragmentar_mensagem(mensagem)

    base = 0
    proximo = 0
    janela = {}

    while base < len(pacotes):
        while proximo < base + JANELA and proximo < len(pacotes):
            payload = pacotes[proximo]
            checksum = calcular_checksum(payload)
            erro_simulado = SIMULAR_ERRO and random.random() < 0.2
            perda_simulada = SIMULAR_PERDA and random.random() < 0.2

            if erro_simulado:
                checksum += 1 

            pacote = {
                "seq_num": proximo,
                "payload": payload,
                "checksum": checksum
            }

            if not perda_simulada:
                s.sendall((json.dumps(pacote) + '\n').encode())
                print(f"[ENVIADO] Seq {proximo} - Payload '{payload}' - ErroSimulado={erro_simulado}")
            else:
                print(f"[PERDA SIMULADA] Seq {proximo} - Payload '{payload}'")

            janela[proximo] = (pacote, time.time())
            proximo += 1

        try:
            s.settimeout(0.5)
            dados = s.recv(1024).decode()
            for linha in dados.strip().split('\n'):
                if not linha: continue
                resposta = json.loads(linha)

                if 'acks' in resposta:
                    for ack_seq in resposta["acks"]:
                        print(f"[ACK GRUPO] recebido {ack_seq}")
                        if ack_seq in janela:
                            del janela[ack_seq]
                elif 'nacks' in resposta:
                    for nack_seq in resposta["nacks"]:
                        print(f"[NACK] recebido {nack_seq} — reenviando")
                        pacote = janela[nack_seq][0]
                        s.sendall((json.dumps(pacote) + '\n').encode())
            while base not in janela and base < proximo:
                base += 1

        except socket.timeout:
            now = time.time()
            for seq, (pacote, t) in list(janela.items()):
                if now - t > TEMPO_TIMEOUT:
                    print(f"[TIMEOUT] Reenviando pacote {seq}")
                    s.sendall((json.dumps(pacote) + '\n').encode())
                    janela[seq] = (pacote, time.time())

    print("Todos os pacotes foram enviados e confirmados.")
    s.sendall("sair\n".encode())
    s.close()

if __name__ == "__main__":
    main()
