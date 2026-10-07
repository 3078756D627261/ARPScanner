# ⚜️ ARP Scanner - Python Raw Sockets
[![GitHub](https://img.shields.io/badge/github-repo-3776AB?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![ARP](https://img.shields.io/badge/Protocol-ARP-00A67E?style=for-the-badge)](https://img.shields.io/)
[![LAYER](https://img.shields.io/badge/Layer-2-orange?style=for-the-badge)](https://img.shields.io/)
[![OS](https://img.shields.io/badge/Platform-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black")](https://img.shields.io/)
[![LAB](https://img.shields.io/badge/Security-Lab-8A2BE2?style=for-the-badge)]("https://github.com/3078756D627261/ARPScanner/")

A lightweight ARP-based network host discovery tool written in Python. Built from raw sockets to explore how Ethernet frames and ARP packets work under the hood.

---

## ⚠️ Disclaimer
> [!WARNING]
> This project was created for educational purposes, particularly to better understand how ARP packets are constructed, encapsulated inside Ethernet frames, transmitted through raw sockets, and parsed from received responses. Use this tool only on networks and systems you own or have explicit permission to test.

---

## 📖 About

ARP Scanner is a small educational network discovery tool that uses `ARP (Address Resolution Protocol)` and `Linux raw sockets` to identify active IPv4 hosts on a local network. Instead of relying on high-level networking libraries, the project manually constructs:

```text
Ethernet Frame
      │
      └── ARP Request
```
and sends the resulting frame directly through a network interface.

---

## ✨ Features

- 🔎 ARP-based host discovery
- ⚡ Raw Ethernet packet construction
- 📡 Linux AF_PACKET raw sockets
- 🧩 Manual ARP packet encoding
- 📦 Manual Ethernet frame construction
- 📥 ARP response parsing
- 🖥️ IP + MAC address discovery
- 🌐 Custom network interface
- 🎯 Custom IPv4 subnet
- 🐍 Pure Python implementation

---

## 🧠 How It Works

The scanner sends an ARP request to each usable address in the selected subnet.

For example:

```text
192.168.1.0/24
```

produces:

```text
192.168.1.1
192.168.1.2
192.168.1.3
       ...
192.168.1.254
```

For each address, it creates an Ethernet frame containing an ARP request. The request essentially asks:

```text
Who has 192.168.1.X?
```
A host that owns that address can respond:

```text
192.168.1.X is at AA:BB:CC:DD:EE:FF
```
The scanner then extracts the responding host's:

```text
IPv4 address
MAC address
```
and displays them.

---

## 🧱 Packet Structure

The project manually constructs the following layers:

```text
┌────────────────────────────────────────────┐
│              Ethernet Header               │
├────────────────────────────────────────────┤
│               ARP Header                   │
├────────────────────────────────────────────┤
│              ARP Payload                   │
└────────────────────────────────────────────┘
```

### Ethernet Header

The Ethernet header contains:

| Field	| Size |
|---|---|
| Destination MAC |	6 bytes |
| Source MAC |	6 bytes |
| EtherType |	2 bytes |

For ARP:

```text
EtherType = 0x0806
```

The destination MAC address is the Ethernet broadcast address:

```text
ff:ff:ff:ff:ff:ff
```

This allows the ARP request to reach other hosts on the local Layer 2 network.

### ARP Header

The ARP request contains:

| Field	| Size |
|---|---|
| Hardware Type |	2 bytes |
| Protocol Type |	2 bytes |
| Hardware Address Length |	1 byte |
| Protocol Address Length |	1 byte |
| Opcode |	2 bytes |
| Sender MAC |	6 bytes |
| Sender IP |	4 bytes |
| Target MAC |	6 bytes |
| Target IP |	4 bytes |

For Ethernet/IPv4 ARP:

```text
Hardware Type            = 1
Protocol Type            = 0x0800
Hardware Address Length  = 6
Protocol Address Length  = 4
Opcode                   = 1
```

Where:

```text
Opcode 1 = ARP Request
Opcode 2 = ARP Reply
```

---

## 🧩 Raw Sockets

One of the most important parts of the project is the raw socket:

```text
socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806))
```

Unlike a normal TCP or UDP socket, this operates at the `data-link layer`.

```text
┌─────────────────────────┐
│       Application       │
├─────────────────────────┤
│         TCP/UDP         │
├─────────────────────────┤
│          IPv4           │
├─────────────────────────┤
│      Ethernet / ARP     │ ◄── This project
├─────────────────────────┤
│     Network Interface   │
└─────────────────────────┘
```

`AF_PACKET` is a Linux-specific socket family that allows applications to work with packets at the data-link layer. This gives the program direct access to Ethernet frames rather than requiring TCP or UDP.

The socket is bound to the selected network interface:

```text
socket_obj.bind((iface, 0))
```

For example:

```text
eth0
wlan0
enp3s0
```

---

## 🗂️ Project Architecture

The script is intentionally kept simple and consists of several focused functions:

```text
ARPScanner.py
│
├── banner()
│
├── get_ip_addr()
├── get_mac_addr()
│
├── convert_ip_to_bytes()
├── convert_mac_to_bytes()
│
├── ethernet_encapsulation()
├── arp_encapsulation()
│
├── socket_creation()
├── socket_binding()
│
├── send_arp_request()
├── recv_arp_response()
│
├── arp_decapsulation()
│
└── main()
```

### Function Overview

| Function | Purpose |
|---|---|
| `banner()` | Displays the application banner |
| `arp_encapsulation()` |	Builds the ARP request |
| `ethernet_encapsulation()` | Builds the Ethernet header |
| `socket_creation()` |	Creates the raw socket |
| `socket_binding()` | Binds the socket to an interface |
| `send_arp_request()` | Sends the ARP request |
| `recv_arp_response()` |	Receives an ARP response |
| `arp_decapsulation()` |	Extracts information from an ARP response |
| `get_ip_addr()` |	Retrieves the interface IPv4 address |
| `get_mac_addr()` | Retrieves the interface MAC address |
| `convert_ip_to_bytes()` |	Converts an IPv4 address to bytes |
| `convert_mac_to_bytes()` | Converts a MAC address to bytes |
| `main()` | Controls the scanning process |

---

## ⚙️ Requirements

### Operating System

This project is designed for:

```text
🐧 Linux
```

The implementation relies on:

```text
socket.AF_PACKET
```

which is a Linux-specific packet interface.

> [!IMPORTANT]
> `AF_PACKET` is not available on standard Windows sockets.

### Python

Python 3 is required.

Check your version:

```text
python3 --version
```

### Dependency

The only external Python dependency is:

```text
psutil
```

Install it with:

```text
python3 -m pip install psutil
sudo apt-get install python3-psutil
```

---

## 🎯 Usage

Clone the repository:

```text
git clone https://github.com/3078756D627261/ARPScanner.git
cd ARPScanner
```

Raw packet access normally requires elevated privileges.

Run:

```text
sudo python3 ARPScanner.py
```

The default configuration is:

```text
Interface → eth0
Network   → 192.168.1.0/24
```

Specify an Interface

```text
sudo python3 ARPScanner.py -i eth0
```
For a wireless interface:

```text
sudo python3 ARPScanner.py -i wlan0
```

Specify a Network

```text
sudo python3 ARPScanner.py -i eth0 -r 192.168.1.0/24
```

Example:

```text
sudo python3 ARPScanner.py -i eth0 -r 10.0.0.0/24
```

Show Help

```text
python3 ARPScanner.py --help
```

---

## 🖥️ Example

```text
╭──────────────────────────────────────────╮
│             ARP Scanner v1.0             │
╰──────────────────────────────────────────╯

[•] Sniffing ARP Reply from 1-254 (Be Patient)...

aa:bb:cc:dd:ee:ff → 192.168.1.1
11:22:33:44:55:66 → 192.168.1.10
de:ad:be:ef:12:34 → 192.168.1.25
```

Each discovered host is displayed as:

```text
MAC Address → IP Address
```

---

## 🔄 Scan Workflow

```text
                 ┌─────────────────┐
                 │  Choose Network │
                 │    Interface    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Determine Local │
                 │ IP + MAC Address│
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Generate Target │
                 │   IP Addresses  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Build Ethernet │
                 │      Header     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │    Build ARP    │
                 │     Request     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Send via Raw  │
                 │      Socket     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Wait for ARP  │
                 │     Response    │
                 └────────┬────────┘
                          │
                    ┌─────┴─────┐
                    │           │
                  Reply       Timeout
                    │           │
                    ▼           ▼
              Extract IP/MAC   Ignore
                    │
                    ▼
              Display Host
```

---

## 🔬 Understanding `struct`

The project uses Python's `struct` module to convert between Python values and binary packet fields.

For example:

```text
struct.pack("!H", 1)
```

The `!` means:

```text
Network byte order / Big Endian
```
The `H` represents:

```text
Unsigned short
```

The ARP response is later parsed using:

```text
struct.unpack("!HHBBH6s4s6s4s", arp_header[14:42])
```

This is a useful example of how protocol specifications can be translated directly into binary parsing logic.

---

## ⚠️ Limitations

This project is intentionally simple and is designed for learning rather than production use.

### Local Network Discovery

ARP is a Layer-2 protocol and normally operates within the local broadcast domain.

It does not provide general Internet-wide host discovery.

```text
                 Local Network
                      │
          ┌───────────┼───────────┐
          │           │           │
        Host A      Host B      Host C
          │           │           │
          └───────────┼───────────┘
                      │
                    Router
                      │
                 Other Network
```

ARP requests do not normally cross the router.

### Sequential Scanning

The current implementation scans hosts sequentially. The program sends one ARP request and waits for a response before moving to the next address.

It waits up to:

```text
socket_obj.settimeout(0.5) # 0.5 seconds
```

for each response. As a result, scanning larger networks can take longer.

### Socket Creation

A new raw socket is created for each target address.

This keeps the implementation easy to understand but is not optimal for performance.

### IPv4 Only

The implementation is designed around IPv4 ARP.

```text
Protocol Type = 0x0800
```

It does not implement IPv6.

> [!TIP]
> IPv6 uses **Neighbor Discovery Protocol (NDP)** instead of **ARP**.

### Network Configuration

Results may vary depending on:

- Firewalls
- LANs
- Wireless client isolation
- Network segmentation
- Host configuration
- ARP filtering
