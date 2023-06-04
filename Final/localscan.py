import json
import scapy.all
import nmap
import socket
import os
import netifaces
import mac_vendor_lookup
import psutil

#nmap_path = [r"D:\Utility\Nmap\nmap.exe"]
nmap_path = [r"/usr/bin/nmap"]
nmScan = nmap.PortScanner(nmap_search_path=nmap_path)
current_folder = os.getcwd()


def get_local_ip_address():
    """
    Finds local ip address and returns it.
    -> str = ip_address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address


def get_local_mac_address():
    """
    Finds local mac address and returns it.
    -> str: mac_address
    """
    mac_address = []
    for interface in psutil.net_if_addrs():
        if psutil.net_if_addrs()[interface][0].address:
            mac_address.append(psutil.net_if_addrs()[interface][0].address)
    return mac_address


def get_default_gateway():
    """
    Finds the default gateway and returns it.
    -> str: default_gateway
    """
    gateways = netifaces.gateways()
    default_gateway = gateways['default'][netifaces.AF_INET][0]
    return default_gateway


def mac_lookup(mac_address):
    """Finds mac information for the device and returns it
    mac_address: str = 'ac:8b:a9:32:83:ad'
    -> str: mac_address lookup
    """
    return mac_vendor_lookup.MacLookup().lookup(mac_address)


def find_devices(target_network):
    """
    Finds all devices on the target network and returns ips and mac address.
    target_network: str = '192.168.1.0/24'
    return -> device list
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
    -> list: open_ports
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


def network_scan(target_network=f'{get_default_gateway()}/24',
                 port_scan=False,
                 port_range="0-65535",
                 port_scan_speed="T3",
                 os_scan=False,
                 exclude_own_ip=True,
                 exclude_other_ip="",
                 company_name=""
                 ):
    """Starts network scan on a given network. Gives results in a json file.
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
    if exclude_own_ip is True:
        for i in get_local_mac_address():
            try:
                devices.remove((f"{get_local_ip_address()}".lower(),
                                str(i).lower().replace('-',
                                ":")))
                print("Deleted ip")
                break
            except:
                continue
    for i in devices:

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
                            'operating_system': nmScan[i[0]]["osmatch"][0]["name"],
                            'os_Vendor': nmScan[i[0]]["osmatch"][0]["osclass"][0]["vendor"],
                            "os_family": nmScan[i[0]]["osmatch"][0]["osclass"][0]["osfamily"],
                            "accuracy": nmScan[i[0]]["osmatch"][0]["accuracy"]
                            }

            else:
                os_system = "Not Tested"
            if i[0] == default_gateway:
                device_type = "Router - Default gateway"
            else:
                try:
                    if os_system != "Not Tested" and os_system["Vendor"] == "Apple" or os_system["Vendor"] == "Windows":
                        device_type = "Workstation"
                except:
                    device_type = "Not identified"
            try:
                nmScan.scan(i[0])
                clients.append({'host': nmScan[i[0]].hostname(),
                                'ip': i[0],
                                'mac': i[1],
                                'system_vendor': mac_lookup(i[1]),
                                'state': nmScan[i[0]].state(),
                                'device_type': device_type,
                                'operating_system': os_system,
                                'open_ports': open_ports})
            except:
                print("failing to append")
                continue
        except:
            print("failed")
            continue
    with open(f"{current_folder}/scan-results/{company_name}_local_scan.json", "w") as outfile:
        outfile.write(json.dumps(clients))
