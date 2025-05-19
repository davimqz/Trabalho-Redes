import socket
import time
import json

def calcular_checksum(payload):
    return sum(ord(c) for c in payload)

def iniciar_servidor():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 9000))
        server_socket.listen(1)
        print("Servidor iniciado. Aguardando conexão...")

        conn, addr = server_socket.accept()
        print(f"\nConexão estabelecida com: {addr}")

        handshake = json.loads(conn.recv(1024).decode())
        print(f"Handshake recebido:  {handshake}")

        modo = handshake.get("modo_operacao", "individual")
        grupo_max = handshake.get("tam_max", 6)
        
        conn.sendall(json.dumps({
            "status": "sucesso",
            "mensagem": "Conexão estabelecida com ACK em grupo" if modo == "grupo" else "ACK individual"
        }).encode())

        buffer_recebido = {}
        ack_pendentes = set()
        tempo_ack = time.time()


        while True:
            dado = conn.recv(1024).decode()
            if not dado or dado.lower() == "sair":
                break

            try:
                pacote = json.loads(dado)
                seq = pacote["seq_num"]
                payload = pacote["payload"]
                checksum = pacote["checksum"]

                print(f"[RECEBIDO] Seq {seq} - Payload '{payload}'")

                if checksum == calcular_checksum(payload):
                    buffer_recebido[seq] = payload
                    ack_pendentes.add(seq)
                else:
                    print(f"[ERRO CHECKSUM] Pacote {seq}")
                if modo == "grupo":
                    if len(ack_pendentes) >= grupo_max or (time.time() - tempo_ack > 2):
                        conn.sendall(json.dumps({"acks": list(ack_pendentes)}).encode())
                        print(f"[ACK GRUPO] Enviados: {ack_pendentes}")
                        ack_pendentes.clear()
                        tempo_ack = time.time()
                else:
                    conn.sendall(json.dumps({"acks": [seq]}).encode())
                    print(f"[ACK INDIV] Enviado: {seq}")

            except json.JSONDecodeError:
                print("[MALFORMADO] Pacote inválido")

        mensagem_ordenada = ''.join(buffer_recebido[k] for k in sorted(buffer_recebido))
        print(f"\n[FINAL] Mensagem reconstruída: {mensagem_ordenada}")

    except Exception as e:
        print(f"[ERRO SERVIDOR] {e}")
    finally:
        conn.close()
        server_socket.close()
        print("Conexão encerrada")
if __name__ == "__main__":
    iniciar_servidor()