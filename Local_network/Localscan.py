import json
import scapy.all
import nmap
import socket
import uuid
import os
import netifaces
from scapy.layers.inet import IP, ICMP

nmap_path = [r"D:\Utility\Nmap\nmap.exe"]
nmScan = nmap.PortScanner(nmap_search_path=nmap_path)
current_folder = os.getcwd()


def get_local_ip_address():
    """
    Finds local ip address and returns it.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address


def get_local_mac_address():
    """
    Finds local mac address and returns it.
    """
    mac_address = uuid.getnode()
    mac_address = ':'.join(('%012X' % mac_address)[i:i+2]
                           for i in range(0, 12, 2))
    return mac_address
   

def get_default_gateway():
    """
    Finds the default gateway and returns it.
    """
    gateways = netifaces.gateways()
    default_gateway = gateways['default'][netifaces.AF_INET][0]
    return default_gateway


def find_devices(target_network):
    """
    Finds all devices on the target network and returns ips and mac address.
    target_network: str = '192.168.1.0/24'
    """
    devices = []
    arp = scapy.all.ARP(pdst=target_network)
    ether = scapy.all.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = scapy.all.srp(packet, timeout=3, verbose=0)[0]
    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc
        devices.append((ip, mac))
    return devices


def find_open_ports(**kwargs):
    """
    Finds open ports for the given device and returns results.
    ip_adress: str = '192.168.1.1'
    ports: str = '0-65535'
    scan_speed: str = 'T1'/'T5'
    """

    ip = kwargs["ip_adress"]
    nmScan.scan(ip, kwargs['ports'], arguments=f"-{kwargs['scan_speed']}")
    open_ports = []
    for host in nmScan.all_hosts():
        for proto in nmScan[host].all_protocols():
            lport = nmScan[host][proto].keys()
            for port in lport:
                open_ports.append((port, nmScan[host][proto][port]['state']))
    return open_ports


def network_scan(target_network='192.168.1.0/24',
                 port_scan=False,
                 port_range="0-65535",
                 port_scan_speed="T3",
                 os_scan=False,
                 include_own_ip=False):
    """Starts network scan on a given network.
    target_network: str = '192.168.1.0/24',
    port_scan: bool = False,
    port_range: str = '0-65535',
    port_scan_speed: str = 'T3',
    os_scan: bool = False,
    include_own_ip: bool = False,
    """
    clients = []
    devices = find_devices(target_network)
    default_gateway = get_default_gateway()
    if include_own_ip is not True:
        devices.remove((
            f"{get_local_ip_address()}".lower(),
            f"{get_local_mac_address()}".lower()))
   
    for i in devices:
        print(i)
        try:
            if port_scan is True:
                open_ports = find_open_ports(
                    ip_adress=i[0],
                    ports=port_range,
                    scan_speed=port_scan_speed)
            else:
                open_ports = "Not Tested"
            if os_scan is True:
                nmScan.scan(i[0], arguments="-O")
                os_system = {
                            'Operating_system': nmScan[i[0]]["osmatch"][0]["name"],
                            'vendor': nmScan[i[0]]["osmatch"][0]["osclass"][0]["vendor"],
                            "osfamily": nmScan[i[0]]["osmatch"][0]["osclass"][0]["osfamily"],
                            "accuracy": nmScan[i[0]]["osmatch"][0]["accuracy"]
                            }

            else:
                os_system = "Not Tested"
            if i[0] == default_gateway:
                device_type = "Router - Default gateway"
            else:
                if os_system != "Not Tested" and os_system["vendor"] != "Linux":
                    device_type = "Workstation"
                else:
                    device_type = "Not identified"
            try:
                nmScan.scan(i[0])
                clients.append({'host': nmScan[i[0]].hostname(),
                                'ip': i[0],
                                'mac': i[1],
                                'state': nmScan[i[0]].state(),
                                'device_type': device_type,
                                'Operating_system': os_system,
                                'open_ports': open_ports})
            except:
                continue
        except:
            continue
    with open(f"{current_folder}/final/Scan-results/network-scan.json", "w") as outfile:
        outfile.write(json.dumps(clients))


network_scan(target_network="192.168.1.0/24",
             port_scan=True,
             os_scan=True,
             port_range="0-400")
