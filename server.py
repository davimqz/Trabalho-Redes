import socket
import json
import time

def calcular_checksum(payload):
    return sum(ord(c) for c in payload)

def iniciar_servidor():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 9000))
        server_socket.listen(1)
        print("Servidor iniciado. Aguardando conexão...")

        conn, addr = server_socket.accept()
        print(f"Conexão estabelecida com: {addr}")

        handshake = json.loads(conn.recv(1024).decode())
        print(f"Handshake recebido: {handshake}")
        modo = handshake.get("modo_operacao", "individual")
        grupo_max = handshake.get("tam_max", 6)

        conn.sendall((json.dumps({
            "status": "sucesso",
            "mensagem": "ACK individual" if modo == "individual" else "ACK em grupo"
        }) + '\n').encode())

        buffer_recebido = {}
        ack_pendentes = set()
        nack_pendentes = set()
        tempo_ack = time.time()

        while True:
            try:
                conn.settimeout(0.5)
                dado = conn.recv(1024).decode()
                if not dado or dado.lower().strip() == "sair":
                    break

                for linha in dado.strip().split('\n'):
                    if not linha:
                        continue
                    try:
                        pacote = json.loads(linha)
                        seq = pacote["seq_num"]
                        payload = pacote["payload"]
                        checksum = pacote["checksum"]

                        print(f"[RECEBIDO] Seq {seq} - Payload '{payload}'")

                        if checksum == calcular_checksum(payload):
                            buffer_recebido[seq] = payload
                            ack_pendentes.add(seq)
                        else:
                            print(f"[ERRO CHECKSUM] Pacote {seq}")
                            nack_pendentes.add(seq)

                        if modo == "grupo":
                            if len(ack_pendentes) >= grupo_max or (time.time() - tempo_ack > 2):
                                conn.sendall((json.dumps({"acks": list(ack_pendentes)}) + '\n').encode())
                                print(f"[ACK GRUPO] {ack_pendentes}")
                                ack_pendentes.clear()
                                tempo_ack = time.time()
                            if nack_pendentes:
                                conn.sendall((json.dumps({"nacks": list(nack_pendentes)}) + '\n').encode())
                                nack_pendentes.clear()
                        else:
                            if seq in ack_pendentes:
                                conn.sendall((json.dumps({"acks": [seq]}) + '\n').encode())
                            if seq in nack_pendentes:
                                conn.sendall((json.dumps({"nacks": [seq]}) + '\n').encode())

                    except json.JSONDecodeError:
                        print("[MALFORMADO] Pacote inválido")

            except socket.timeout:
                pass 

        mensagem_ordenada = ''.join(buffer_recebido[k] for k in sorted(buffer_recebido))
        print(f"\n[MENSAGEM FINAL] {mensagem_ordenada}")

    except Exception as e:
        print(f"[ERRO SERVIDOR] {e}")
    finally:
        conn.close()
        server_socket.close()
        print("Conexão encerrada")

if __name__ == "__main__":
    iniciar_servidor()
