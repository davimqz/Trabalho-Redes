
# 💬 Sistema Cliente-Servidor com Transporte Confiável (Camada de Aplicação)

## 🎯 Objetivo

Simular um sistema confiável de transporte de dados sobre **sockets TCP**, tratando perda e erro de pacotes diretamente na **camada de aplicação**, implementando características típicas da camada de transporte.

---

## 🧠 Conceitos-Chave Implementados

- Fragmentação de mensagens
- Envio com janela (paralelismo)
- Checksum (verificação de integridade)
- Simulação de perda e erro
- ACK individual e em grupo
- Reenvio após timeout
- Reconstrução da mensagem no destino

---

## 📦 Formato dos Pacotes

```json
{
  "seq_num": 0,
  "payload": "abc",
  "checksum": 294
}
```

## 🧩 Modo de Uso


Em dois terminais, colocar os comandos:

No Primeiro Terminal: 
```
python server.py
```

No Segundo:
```
python client.py