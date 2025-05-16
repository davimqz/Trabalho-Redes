import socket
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

        handshake_data = conn.recv(1024).decode()
        if not handshake_data:
            raise ValueError("Nenhum dado recebido do cliente")

        handshake = json.loads(handshake_data)
        print("\nParâmetros recebidos:")
        print(f"Modo de operação: {handshake.get('modo_operacao')}")
        print(f"Tamanho máximo: {handshake.get('tam_max')}")
        print(f"Versão do protocolo: {handshake.get('versao_protocolo')}")

        resposta = {
            "status": "sucesso",
            "mensagem": "Conexão estabelecida com sucesso",
            "parametros_aceitos": handshake
        }
        conn.sendall(json.dumps(resposta).encode())

        while True:
            mensagem = conn.recv(1024).decode()
            if not mensagem or mensagem.lower() == 'sair':
                break
            
            print(f"\nCliente diz: {mensagem}")
            
            resposta = f"Mensagem recebida: '{mensagem}'"
            conn.sendall(resposta.encode())

    except json.JSONDecodeError:
        print("Erro: Dados recebidos não são JSON válido")
    except Exception as e:
        print(f"Erro no servidor: {str(e)}")
    finally:
        conn.close()
        server_socket.close()
        print("\nConexão encerrada")

if __name__ == "__main__":
    iniciar_servidor()