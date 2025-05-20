
import socket
import time

def print_title(text):
    border = '+' + '-' * (len(text) + 2) + '+'
    print('\n' + border)
    print(f'| {text} |')
    print(border + '\n')

def process_handshake(client_socket):
    print_title("SERVER ← HANDSHAKE")
    print("SERVER: waiting for SYN…")
    syn = client_socket.recv(1024).decode('utf-8')
    print(f"CLIENT → {syn}")

    parts = syn.split("|")
    if parts[0] == "SYN" and len(parts) == 3:
        mode = parts[1]
        max_size = int(parts[2])

        synack = f"SYN-ACK|{mode}|{max_size}"
        print(f"SERVER → sending: {synack}")
        client_socket.send(synack.encode('utf-8'))

        print("SERVER: waiting for ACK…")
        ack = client_socket.recv(1024).decode('utf-8').strip()
        if ack == "ACK":
            print_title("HANDSHAKE COMPLETE")
            return mode, max_size

    client_socket.send(b"ERROR")
    print_title("HANDSHAKE FAILED")
    return None, None

def receive_full_message(conn):
    full = b''
    while b'\n' not in full:
        chunk = conn.recv(1024)
        if not chunk:
            return full
        full += chunk
    return full.split(b'\n')[0]

def receive_stop_and_wait(client_socket):
    print_title("STARTING STOP-AND-WAIT RECEPTION")
    full_message = ""
    expected = 1

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            segment = data.decode('utf-8')
            parts = segment.split('|', 1)
            if len(parts) == 2:
                num = int(parts[0])
                payload = parts[1]
                print(f"\nSERVER: Received segment {num}: '{payload}'")
                if num == expected:
                    full_message += payload
                    ack = f"{num}\n"
                    client_socket.send(ack.encode('utf-8'))
                    print(f"SERVER → sent ACK {num}")
                    expected += 1
                else:
                    print(f"SERVER: Unexpected (expected {expected}, got {num})")
            else:
                print(f"SERVER: Invalid format: {segment}")
        except Exception as e:
            print(f"SERVER error: {e}")
            break

    print_title("STOP-AND-WAIT COMPLETE")
    print(f"Full message: {full_message}\n")

def receive_gobackn(client_socket):
    print_title("STARTING GO-BACK-N RECEPTION")
    buffer = {}
    expected = 1

    while True:
        try:
            data = receive_full_message(client_socket)
            if not data:
                break
            segment = data.decode('utf-8')
            parts = segment.split('|', 1)
            if len(parts) == 2:
                num = int(parts[0])
                payload = parts[1]
                print(f"\nSERVER: Received segment {num}: '{payload}'")

                if num > expected:
                    buffer[num] = payload
                    nack = f"{expected-1}\n"
                    client_socket.send(nack.encode())
                    print(f"SERVER → resent ACK {expected-1}")
                elif num < expected:
                    client_socket.send(f"{num}\n".encode())
                    print(f"SERVER → resent ACK {num}")
                else:
                    buffer[num] = payload
                    client_socket.send(f"{num}\n".encode())
                    print(f"SERVER → sent ACK {num}")
                    expected += 1
                    while expected in buffer:
                        print(f"SERVER: Delivering buffered {expected}")
                        expected += 1
            else:
                print(f"SERVER: Invalid format: {segment}")
        except Exception as e:
            print(f"SERVER error: {e}")
            break

    full_message = "".join(buffer[i] for i in sorted(buffer))
    print_title("GO-BACK-N COMPLETE")
    print(f"Full message: {full_message}\n")

def server():
    host = '127.0.0.1'
    port = 8080

    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind((host, port))
    serv.listen(1)
    print(f"SERVER: listening on {host}:{port}")

    client_sock, addr = serv.accept()
    mode, max_size = process_handshake(client_sock)

    if mode and max_size:
        print(f"SERVER: client {addr} connected in '{mode}', max size {max_size}")
        if mode == "GoBackN":
            receive_gobackn(client_sock)
        else:
            receive_stop_and_wait(client_sock)

    client_sock.close()

if __name__ == '__main__':
    server()
