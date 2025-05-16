import socket
import json
import random

PROBABILIDADE_ERRO = 0.2
PROBABILIDADE_PERDA = 0.1
TIMEOUT = 2
TAMANHO_PACOTE = 3



def fragmentar_mensagem(mensagem):
    pacotes = []
    for i in range (0, len(mensagem), TAMANHO_PACOTE):
        payload = mensagem[i: i + TAMANHO_PACOTE]
        pacotes.append(payload)
    return pacotes

def calcular_checksum(payload):
    return sum(ord(c) for c in payload)

'''
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
'''

def iniciar_cliente():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(TIMEOUT)
        client_socket.connect(('localhost', 9000))
        print("Conectado ao servidor")

        handshake = {
            "modo_operacao": "grupo",
            "tam_max": 6,
            "versao_protocolo": "1.0"
        }
        
        '''
        print("\nParâmetros enviados:")
        print(f"Modo: {parametros['modo_operacao']}")
        print(f"Tamanho máximo: {parametros['tam_max']}")
        print(f"Versão: {parametros['versao_protocolo']}")
        '''
       
        client_socket.sendall(json.dumps(handshake).encode())
        print("Handashake enviado")

    
        resposta = client_socket.recv(1024).decode()
        print("Resposta ao servidor: ", resposta)


        '''
        dados_resposta = json.loads(resposta)
        print(f"\nResposta do servidor: {dados_resposta['mensagem']}")
        print(f"Status: {dados_resposta['status']}")
        '''

        while True:
            mensagem = input("\nDigite sua mensagem ou 'sair' para encerrar: ")
            
            if mensagem.lower() == 'sair':
                client_socket.sendall("sair".encode())
                break
            
            pacotes = fragmentar_mensagem(mensagem)
            seq = 0
            enviados = []

            while seq < len(pacotes):
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
                    print(f"[Simulação] Pacote {seq} enviado com ERRO de integridade")

                if perda:
                    print(f"[Simulação] Pacote {seq} não enviado ao servidor")
                else:
                    print(f"Pacote sendo enviado {seq}: {pacote}")
                    client_socket.sendall(json.dumps(pacote).encode())

                try:
                    resposta = client_socket.recv(1024).decode()
                    resposta_json = json.loads(resposta)

                    if resposta_json['status'] == 'ACK':
                        print(f"Pacote {seq} confirmado")
                        seq += 1
                    else:
                        print(f"Pacote {seq} corrompido")
                except socket.timeout:
                    print(f"Timeout no pacote {seq}")

    except ConnectionRefusedError:
        print("Erro: Não foi possível conectar ao servidor")
    except Exception as e:
        print(f"Erro no cliente: {str(e)}")
    finally:
        client_socket.close()
        print("Conexão encerrada")

if __name__ == "__main__":
    iniciar_cliente()