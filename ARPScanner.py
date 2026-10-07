#! /usr/bin/python3

import argparse
import sys
import psutil
import socket
import ipaddress
import struct

# Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def banner():
    print(f"""
    {CYAN}{BOLD}
╭──────────────────────────────────────────╮
│             ARP Scanner v1.0             │
╰──────────────────────────────────────────╯
    {RESET}""")

def arp_decapsulation(arp_header):
    # Unpacking the ARP header 
    packet = struct.unpack("!HHBBH6s4s6s4s", arp_header[14:42])

    return {
    "sender_mac":":".join(f"{b:02x}" for b in packet[5]),
    "sender_ipaddr":".".join(map(str, packet[6]))
    }

def recv_arp_response(socket_obj):
    try:
        # Receiving an ARP response 
        socket_obj.settimeout(0.5)
        arp_response_header = socket_obj.recv(65535)
        return arp_response_header
    except socket.timeout:
        return None
    except socket.error as arp_response_error:
        print(f"{RED}[x] Failed to receive ARP response: {arp_response_error}{RESET}")
        socket_obj.close()
        sys.exit(1)

def send_arp_request(binded_socket_obj, arp_header):
    try:
        # Sending an ARP request
        binded_socket_obj.send(arp_header)
        return True
    except socket.error as arp_request_error:
        print(f"{RED}[x] Failed to send ARP request: {arp_request_error}{RESET}")
        binded_socket_obj.close()
        sys.exit(1)

def arp_encapsulation(ethernet_frame, src_mac, src_ipaddr, dst_ipaddr):
    """ +----------------------------------------------------------------------------------------+
        |                Hardware type                      |            Protocol type           |
        +----------------------------------------------------------------------------------------+
        | Hardware address length | Protocol address length |               Opcode               |
        +----------------------------------------------------------------------------------------+
        |                               Source hardware address                                  |
        +----------------------------------------------------------------------------------------+
        |                               Source protocol address                                  |
        +----------------------------------------------------------------------------------------+
        |                               Destination hardware address                             |
        +----------------------------------------------------------------------------------------+
        |                               Destination protocol address                             |
        +----------------------------------------------------------------------------------------+
        |                                         Data                                           |
        +----------------------------------------------------------------------------------------+

        * Hardware type                  : 16
        * Protocol type                  : 16
        * Hardware address length        : 8
        * Protocol address length        : 8
        * Opcode                         : 16
        * Source hardware address        : 48
        * Source protocol address        : 32
        * Destination hardware address   : 48
        * Destination protocol address   : 32"""

    # ARP header fields
    hardware_type = struct.pack("!H", 1)
    protocol_type = struct.pack("!H", 0x800)
    hardware_size = struct.pack("!B", 6)
    protocol_size = struct.pack("!B", 4)
    opcode = struct.pack("!H", 1)

    sender_mac = convert_mac_to_bytes(src_mac)
    sender_ipaddr = convert_ip_to_bytes(src_ipaddr)
    target_mac = convert_mac_to_bytes("00:00:00:00:00:00")
    target_ipaddr = convert_ip_to_bytes(dst_ipaddr)

    # Encapsulation
    arp_header = (
        hardware_type + protocol_type + 
        hardware_size + protocol_size + 
        opcode + sender_mac + sender_ipaddr +
        target_mac + target_ipaddr
    )

    finally_packet = ethernet_frame + arp_header
    return finally_packet

def ethernet_encapsulation(iface_mac):
    """+------------------------------------------------------------------------+
       | Preamble | Destination MAC | Source MAC | Ether Type | User Data | FCS |
       +------------------------------------------------------------------------+
       |    8B    |       6B        |     6B     |     2B     | 46-1500B  | 4B  |
       +------------------------------------------------------------------------+

       * Destination: Broadcast (ff:ff:ff:ff:ff:ff)
       * Source: sender's MAC address
       * Type: ARP (0x0806)"""

    # Convert MAC addresses to bytes
    src_mac_addr = convert_mac_to_bytes(iface_mac)
    dst_mac_addr = convert_mac_to_bytes("ff:ff:ff:ff:ff:ff")

    # Define EtherType for ARP (0x0806)
    ether_type = bytes.fromhex("0806")

    # Encapsulation
    ethernet_header = (
        dst_mac_addr + 
        src_mac_addr + 
        ether_type
    )
    return ethernet_header

def socket_binding(socket_obj, iface):
    try:
        # AF_PACKET raw sockets on Linux, bind() expects the interface name, like "eth0" or "wlan0" — not an IP address.
        # Setting it to 0 means: "Receive all Ethernet protocols" — no filtering.
        socket_obj.bind((iface, 0))
    except socket.error as socket_bind_error:
        print(f"{RED}[x] Socket binding failed with error: {socket_bind_error}{RESET}")
        socket_obj.close()
        sys.exit(1)

def socket_creation():
    try:
        # Creating a raw socket
        # AF_PACKET is a socket family used to create raw sockets that operate at the data link layer (Layer 2) of the OSI model. This allows you to directly send and receive Ethernet frames, giving you full control over the packet structure.
        # The expression socket.htons(0x0806) in Python is used to specify the EtherType for ARP (Address Resolution Protocol) when working with raw sockets at the Ethernet level.
        socket_object = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806))
        return socket_object
    except socket.error as socket_creation_error:
        print(f"{RED}[x] Socket creation failed with error: {socket_creation_error}{RESET}")
        sys.exit(1)

def convert_ip_to_bytes(ipaddr):
    return socket.inet_aton(str(ipaddr))

def convert_mac_to_bytes(mac):
    return bytes.fromhex(mac.replace(":", ""))

def get_ip_addr(iface):
    try:
        # Retrieving network interface information to find the IP address
        iface_info = psutil.net_if_addrs()

        for addr in iface_info.get(iface, []):
            if addr.family == socket.AF_INET:
                return addr.address
        return None
    except Exception as error:
        print(f"{RED}[x] Failed to retrieve the interface's IP address: {error}{RESET}")
        sys.exit(1)

def get_mac_addr(iface):
    try:
        # Retrieving network interface information to find the MAC address
        iface_intel = psutil.net_if_addrs()

        if iface in iface_intel:
            for addr in iface_intel[iface]:
                if addr.family == psutil.AF_LINK:
                    return addr.address
            return None
    except Exception as error:
        print(f"{RED}[x] Failed to retrieve the interface's MAC address: {error}{RESET}")
        sys.exit(1)

def main():
    # Create an argument parser
    # ArgumentDefaultsHelpFormatter ensures default values are shown in the help text
    parser = argparse.ArgumentParser(description="Simple network host discovery using ARP", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Define the command-line arguments
    parser.add_argument("-i", "--iface", metavar="", default="eth0", help="Interface")
    parser.add_argument("-r", "--range", metavar="", default="192.168.1.0/24", help="Subnet")

    # Parse and use the arguments
    args = parser.parse_args()

    # Retrieve the interface's MAC address
    iface_mac = get_mac_addr(args.iface)

    # Retrieve the interface's IP address
    iface_ip = get_ip_addr(args.iface)

    # Generating a range of IP addresses
    network_range = ipaddress.ip_network(args.range)
    ip_list = list(network_range.hosts())

    # Ethernet frame encapsulation
    ethernet_frame = ethernet_encapsulation(iface_mac)

    nodes = []

    try:
        print(f"{YELLOW}[•] Sniffing ARP Reply from 1-254 (Be Patient)...\n{RESET}")
        for dst_ipaddr in ip_list:
            # ARP packet encapsulation
            arp_packet = arp_encapsulation(ethernet_frame, iface_mac, iface_ip, dst_ipaddr)

            # Creating a socket
            socket_obj = socket_creation()

            # Binding the socket
            socket_binding(socket_obj, args.iface)

            # Sending an ARP request
            send_arp_request(socket_obj, arp_packet)

            # Receiving an ARP response
            arp_response = recv_arp_response(socket_obj)

            if arp_response != None:
                info = arp_decapsulation(arp_response)
                if info not in nodes:
                    nodes.append(info)

        for node in nodes:
            print(f"{node["sender_mac"]:<10} {GREEN}→{RESET} {node["sender_ipaddr"]}")

    except KeyboardInterrupt:
        print(f"{RED}[x] Script stopped. You pressed Ctrl+C{RESET}")
        socket_obj.close()
        sys.exit(1)

main()