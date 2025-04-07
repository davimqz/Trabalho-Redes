import socket
import json

def iniciar_cliente():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 9000))
        print("Conectado ao servidor")

        
        parametros = {
            "modo_operacao": "grupo",
            "tam_max": 6,
            "versao_protocolo": "1.0"
        }

        
        client_socket.sendall(json.dumps(parametros).encode())
        print("\nParâmetros enviados:")
        print(f"Modo: {parametros['modo_operacao']}")
        print(f"Tamanho máximo: {parametros['tam_max']}")

       
        resposta = client_socket.recv(1024).decode()
        if not resposta:
            raise ValueError("Nenhuma resposta recebida do servidor")

        dados_resposta = json.loads(resposta)
        print(f"\nResposta do servidor: {dados_resposta['mensagem']}")
        print(f"Status: {dados_resposta['status']}")

        
        while True:
            mensagem = input("\nDigite sua mensagem (ou 'sair' para encerrar): ")
            client_socket.sendall(mensagem.encode())
            
            if mensagem.lower() == 'sair':
                break
            
            
            resposta = client_socket.recv(1024).decode()
            print(f"Servidor respondeu: {resposta}")

    except ConnectionRefusedError:
        print("Erro: Não foi possível conectar ao servidor")
    except Exception as e:
        print(f"Erro no cliente: {str(e)}")
    finally:
        client_socket.close()
        print("Conexão encerrada")

if __name__ == "__main__":
    iniciar_cliente()