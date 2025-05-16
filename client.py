import socket
import json

def calcular_checksum(payload):
    return sum(ord(c) for c in payload)

def obter_parametros():
    print("\nConfiguração de conexão:")
    modo = input("Modo de operação (grupo/individual): ") or "grupo"
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
        client_socket.connect(('localhost', 9000))
        print("Conectado ao servidor")

        parametros = obter_parametros()

        client_socket.sendall(json.dumps(parametros).encode())
        print("\nParâmetros enviados:")
        print(f"Modo: {parametros['modo_operacao']}")
        print(f"Tamanho máximo: {parametros['tam_max']}")
        print(f"Versão: {parametros['versao_protocolo']}")

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
            print(f"Servidor confirmou recebimento: {resposta}")

    except ConnectionRefusedError:
        print("Erro: Não foi possível conectar ao servidor")
    except Exception as e:
        print(f"Erro no cliente: {str(e)}")
    finally:
        client_socket.close()
        print("Conexão encerrada")

if __name__ == "__main__":
    iniciar_cliente()