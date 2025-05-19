import socket
import json
import random
import time

PROBABILIDADE_ERRO = 0.2
PROBABILIDADE_PERDA = 0.1
TIMEOUT = 2
TAMANHO_PACOTE = 3
JANELA_ENVIO = 3
MAX_RETRIES = 5

def calcular_checksum(payload):
    return sum(ord(c) for c in payload)

def fragmentar_mensagem(mensagem):
    return [mensagem[i:i + TAMANHO_PACOTE] for i in range(0, len(mensagem), TAMANHO_PACOTE)]

def obter_parametros():
    print("=== Configuração do Cliente ===")
    modo = input("Modo de operação (individual/grupo): ") or "grupo"
    tam_max = input("Tamanho máximo do grupo (padrão 6): ") or "6"
    versao = input("Versão do protocolo (padrão 1.0): ") or "1.0"
    return {
        "modo_operacao": modo,
        "tam_max": int(tam_max),
        "versao_protocolo": versao
    }

def iniciar_cliente():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(TIMEOUT)
        client_socket.connect(('localhost', 9000))
        print("Conectado ao servidor")

        parametros = obter_parametros()
        client_socket.sendall((json.dumps(parametros) + '\n').encode())
        print("Handshake enviado")

        resposta = client_socket.recv(1024).decode()
        print("Resposta do servidor:", resposta.strip())

        while True:
            mensagem = input("\nDigite sua mensagem ou 'sair' para encerrar: ")
            if mensagem.lower() == 'sair':
                client_socket.sendall("sair".encode())
                break

            pacotes = fragmentar_mensagem(mensagem)
            enviados = {}
            retries = {}
            acked = set()
            base = 0

            while base < len(pacotes):
                while len(enviados) < JANELA_ENVIO and (base + len(enviados)) < len(pacotes):
                    seq = base + len(enviados)
                    payload = pacotes[seq]
                    erro = random.random() < PROBABILIDADE_ERRO
                    perda = random.random() < PROBABILIDADE_PERDA

                    pacote = {
                        "seq_num": seq,
                        "payload": payload,
                        "checksum": calcular_checksum(payload)
                    }

                    if erro:
                        pacote["checksum"] += 1
                        print(f"[ERRO] Pacote {seq} com checksum incorreto")

                    if perda:
                        print(f"[PERDA] Pacote {seq} não enviado")
                        enviados[seq] = pacote
                        retries[seq] = retries.get(seq, 0)
                        continue

                    client_socket.sendall((json.dumps(pacote) + '\n').encode())
                    print(f"[ENVIO] Pacote {seq} enviado: {pacote}")
                    enviados[seq] = pacote
                    retries[seq] = 0

                try:
                    resposta = client_socket.recv(1024).decode()
                    for linha in resposta.strip().split('\n'):
                        if not linha:
                            continue
                        acks = json.loads(linha).get("acks", [])
                        print(f"[ACKs] Recebidos: {acks}")
                        for ack in acks:
                            acked.add(ack)
                            if ack in enviados:
                                del enviados[ack]
                            if ack in retries:
                                del retries[ack]
                    while base in acked:
                        base += 1

                except socket.timeout:
                    print("[TIMEOUT] Reenviando pacotes não confirmados...")
                    for seq, pacote in list(enviados.items()):
                        retries[seq] += 1
                        if retries[seq] > MAX_RETRIES:
                            print(f"[DESCARTE] Pacote {seq} descartado após {MAX_RETRIES} tentativas.")
                            del enviados[seq]
                            acked.add(seq)
                            continue
                        client_socket.sendall((json.dumps(pacote) + '\n').encode())
                        print(f"[REENVIO] Pacote {seq}: {pacote}")

    except Exception as e:
        print(f"[ERRO CLIENTE] {e}")
    finally:
        client_socket.close()
        print("Conexão encerrada")

if __name__ == "__main__":
    iniciar_cliente()
