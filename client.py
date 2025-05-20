# client.py
import socket
import time
import random

def print_title(text):
    border = '+' + '-' * (len(text) + 2) + '+'
    print('\n' + border)
    print(f'| {text} |')
    print(border + '\n')

def handshake(client_socket):
    print_title("CLIENT → HANDSHAKE")
    max_size = 0
    mode = ""
    simulated_error = None

    while True:
        print("CLIENT: select mode:")
        print("  1) GoBackN")
        print("  2) Stop-and-Wait")
        choice = input("Mode [1-2]: ")
        if choice == "1":
            mode = "GoBackN"
            break
        if choice == "2":
            mode = "stop-and-wait"
            break
        print("Invalid choice, try again.\n")

    while True:
        size_input = input("CLIENT: enter max packet size: ")
        if size_input.isdigit() and int(size_input) > 0:
            max_size = int(size_input)
            break
        print("Must be a positive integer.\n")

    while True:
        print("CLIENT: simulate errors?")
        print("  1) Yes")
        print("  2) No")
        sim = input("Choice [1-2]: ")
        if sim == "1":
            err = input("  1) Timeout\n  2) Duplicate packet\nSelect [1-2]: ")
            if err in ("1", "2"):
                simulated_error = err
                break
            print("  Invalid, try again.")
        elif sim == "2":
            break
        else:
            print("Invalid, try again.\n")

    syn = f"SYN|{mode}|{max_size}"
    print(f"CLIENT → sending: {syn}")
    client_socket.send(syn.encode())

    print("CLIENT → waiting SYN-ACK…")
    resp = client_socket.recv(1024).decode()
    print(f"SERVER → {resp}")

    parts = resp.split("|")
    if parts == ["SYN-ACK", mode, str(max_size)]:
        print("CLIENT → sending ACK")
        client_socket.send(b"ACK")
        print_title("HANDSHAKE COMPLETE")
    else:
        print_title("HANDSHAKE FAILED")

    return mode, max_size, simulated_error

def receive_full_message(conn):
    full = b''
    while b'\n' not in full:
        chunk = conn.recv(1024)
        if not chunk:
            return full
        full += chunk
    return full.split(b'\n')[0]

def communicate_gobackn(client_socket, text, max_size, simulated_error):
    print_title("STARTING GO-BACK-N TRANSMISSION")

    segments = {}
    seq_num = 1
    for i in range(0, len(text), max_size):
        segments[seq_num] = text[i:i + max_size]
        seq_num += 1

    print(f">> Original message: {text}")
    for seq, seg in segments.items():
        print(f">>    Segment {seq}: {seg}")

    window_size = 3
    window = {}
    next_seg = 1
    base = 1
    total = len(segments)

    timeout_error_seg = random.randint(1, total) if simulated_error == "1" else None
    dup_error_seg     = random.randint(1, total) if simulated_error == "2" else None

    print(f"\n>> Initial send window (size: {window_size})\n" + "=*" * 40)

    while base <= total:
        print(f"\n>> Sending window starting at base {base}:")

        while len(window) < window_size and next_seg <= total:
            num = next_seg
            seg = segments[num]
            packet = f"{num}|{seg}\n".encode()

            try:
                if simulated_error == "1" and num == timeout_error_seg:
                    print(f"Simulating TIMEOUT on segment {num}")
                    window[num] = (seg, time.time())
                    next_seg += 1
                    continue

                client_socket.send(packet)
                window[num] = (seg, time.time())
                print(f">> Sent segment {num}: '{seg}'")
                next_seg += 1

                if simulated_error == "2" and num == dup_error_seg:
                    print(f"Simulating DUPLICATE on segment {num}")
                    client_socket.send(packet)
                    print(f"\n{packet.decode()} resent\n")

            except socket.error as e:
                print(f">> Error sending segment {num}: {e}")
                break

        print(f"\n>> Current window: {list(window.keys())}")

        if window:
            client_socket.settimeout(10)
            try:
                ack_bytes = receive_full_message(client_socket)
                if not ack_bytes:
                    print(">> Server closed connection.")
                    break
                ack_str = ack_bytes.decode('utf-8')

                if ack_str.isdigit():
                    ack = int(ack_str)
                    print(f"\n>> Received ACK for segment {ack}")
                    if ack >= base:
                        base = ack + 1
                        for k in [k for k in window if k < base]:
                            del window[k]
                        print(f">> Window after ACK: {list(window.keys())}")
                        print(f">> New base: {base}\n" + "=*" * 40)
                    else:
                        print(f">> Stale or invalid ACK: {ack}")
                else:
                    print(f">> Invalid ACK format: '{ack_str}'")

            except socket.timeout:
                print(f">> Timeout awaiting ACK for segment {base}. Resending...")
                for seq in list(window):
                    seg_data, _ = window[seq]
                    pack = f"{seq}|{seg_data}\n".encode()
                    try:
                        client_socket.send(pack)
                        window[seq] = (seg_data, time.time())
                        print(f">> Resent segment {seq}: '{seg_data}'")
                    except socket.error as e:
                        print(f">> Error resending {seq}: {e}")
                        break
        else:
            break

    print_title("GO-BACK-N TRANSMISSION COMPLETE")

def communicate_stop_and_wait(client_socket, text, max_size, simulated_error):
    print_title("STARTING STOP-AND-WAIT TRANSMISSION")

    seq = 1
    total = (len(text) + max_size) // max_size
    error_seg = random.randint(1, total) if simulated_error in ("1","2") else None

    while text:
        data = text[:max_size]
        text = text[max_size:]
        packet = f"{seq}|{data}".encode('utf-8')
        sent = False

        while not sent:
            if simulated_error == "2" and seq == error_seg:
                print(f">> Simulating DUPLICATE on segment {seq}")
                client_socket.send(packet)
                simulated_error = None
            if simulated_error == "1" and seq == error_seg:
                print(f">> Simulating TIMEOUT on segment {seq}")
                time.sleep(3)
                simulated_error = None
            else:
                try:
                    print(f">> Sending segment {seq}: '{data}'")
                    client_socket.send(packet)
                except socket.error as e:
                    print(f">> Error sending: {e}")
                    return

            try:
                client_socket.settimeout(2)
                ack = client_socket.recv(1024).decode('utf-8').strip()
                print(f">> Received ACK: {ack}")
                if ack == str(seq):
                    sent = True
                    seq += 1
                else:
                    print(f">> Wrong ACK. Resending {seq}")
            except socket.timeout:
                print(f">> Timeout on segment {seq}")
            except socket.error as e:
                print(f">> Socket error: {e}")
                return

    try:
        print(">> Sending END signal.")
        client_socket.send(b"END")
    except socket.error as e:
        print(f">> Error sending END: {e}")

    print_title("STOP-AND-WAIT TRANSMISSION COMPLETE")

def start_communication(client_socket, max_size, mode, simulated_error):
    message = input("\nEnter your message (or 'exit' to quit): ")
    if message.lower() == 'exit':
        print("Disconnecting...")
        return

    if mode.upper() == "GOBACKN":
        communicate_gobackn(client_socket, message, max_size, simulated_error)
    elif mode.upper() == "STOP-AND-WAIT":
        communicate_stop_and_wait(client_socket, message, max_size, simulated_error)
    else:
        print("Unknown mode.")

def client():
    host = '127.0.0.1'
    port = 8080

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except ConnectionRefusedError as err:
        print(f">> Connection error: {err}")
        return

    mode, max_size, simulated_error = handshake(sock)
    if mode and max_size:
        start_communication(sock, max_size, mode, simulated_error)

    sock.close()

if __name__ == '__main__':
    client()
