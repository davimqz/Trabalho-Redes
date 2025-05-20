# 💬 Reliable Client-Server Transport System (Application Layer)

## 🎯 Objective

Simulate a **reliable data transport** system over **TCP sockets**, handling packet loss and errors directly at the **application layer**, and demonstrating common transport-layer features.

---

## 🧠 Key Concepts Implemented

* **3-way Handshake** (SYN, SYN-ACK, ACK)
* **Stop-and-Wait** protocol mode
* **Go-Back-N** protocol mode with sliding window
* **Fragmentation** of application messages
* **Timeout and Retransmission** on missing ACKs
* **Duplicate Packet** simulation and handling
* **Buffered Out-of-Order Delivery** for Go-Back-N

---

## 📦 Packet Format

Messages are sent as plain text in the form:

```
<sequence_number>|<payload>\n
```

No explicit checksum is used; error conditions are simulated in-code.

---

## 🧩 How to Use

1. Open two terminal windows.

2. In the first terminal, start the server:

   ```bash
   python server.py
   ```

3. In the second terminal, start the client:

   ```bash
   python client.py
   ```

4. Follow the prompts in the client to:

   * Choose protocol mode (GoBackN or Stop-and-Wait)
   * Set maximum packet size
   * Optionally simulate errors (timeout or duplicate packets)
   * Enter the message to send

---

## ⚙️ Configuration

* **Server host**: `127.0.0.1`
* **Server port**: `8080`
* **Client** connects to the same host and port by default

To change these values, edit the `host` and `port` variables in each script.

---

## 🚀 Execution Flow

1. **Handshake**: client sends `SYN|mode|max_size`, server replies `SYN-ACK|mode|max_size`, client confirms with `ACK`.
2. **Data Transfer**:

   * In **Stop-and-Wait**: send one packet and wait for its ACK before proceeding.
   * In **Go-Back-N**: maintain a sliding window of up to 3 packets, send them and handle cumulative ACKs.
3. **Error Simulation**: client may skip or duplicate a packet to simulate loss or duplication.
4. **Completion**: client sends `END`, server reassembles and prints the full message.

---

