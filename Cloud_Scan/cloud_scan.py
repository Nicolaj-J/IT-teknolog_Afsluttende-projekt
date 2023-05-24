from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
import re
import json


def export_azure_info(client_id, secret, tentant, sub):
    """
    This function establishes a connection to Azure using the Azure SDK compute mgmt and network mgmt libraries.
    The function finds information associated to every virtual machine in Azure which is then exported to a JSON file.
    """

    # CREDENTIALS FOR AZURE DEFINED
    credentials = ServicePrincipalCredentials(client_id=client_id,
                                              secret=secret,
                                              tenant=tentant)

    # SUBSCRIPTION ID FOR AZURE DEFINED
    subscription_id = sub
    # RESULT LIST DEFINED
    result_list = []

    # COMPUTE MNGT CLIENT OBJECT CREATED
    compute_client = ComputeManagementClient(credentials, subscription_id)
    # NETWORK MNGT CLIENT OBJECT CREATED
    network_client = NetworkManagementClient(credentials, subscription_id)

    # COMPUTE CLIENT OBJACT USED TO QUERY ALL VM'S
    vm_list = compute_client.virtual_machines.list_all()

    print("FOUND THE FOLLOWING VM's:")

    # ALL VM'S PROCESSED IN FOR LOOP
    for vm in vm_list:

        # SPLIT VM INFO BY "/" INTO AN ARRAY
        array = vm.id.split("/")
        # DEFINE VM NAME AS LAST VALUE IN ARRAY
        vm_name = array[-1]
        print(f"HOST NAME: {vm_name}")
        # DEFINE RESOURCE GROUP AS 5TH VALUE IN ARRAY
        resource_group = array[4]
        print(f"VM RESOURCE GROUP: {resource_group}")

        # OS TYPE
        # GENERAL OS INFO WINDOWS/LINUX
        os = vm.storage_profile.os_disk.os_type.value
        # SET'S THE OS TYPE AS THE AZURE IMAGAGE NAME
        os_type = vm.storage_profile.image_reference.offer

        # MATCH OS TYPE TO INCLUDE THE WORD SERVER
        if re.match(os_type, "server"):
            device_type = "Server"

        # MATCH OS TYPE TO INCLUDE WINDOWS OR DESKTOP
        elif re.match(os_type, "windows") or re.match(os_type, "desktop"):
            device_type = "Workstation"

        # SET DEFAULT TO UNKNOWN IF NO MATCHES WHERE FOUND
        else:
            device_type = "Unknwon"

        print(f"VM OS: {os}")
        print(f"OS TYPE: {os_type}")
        print(f"DEVICE TYPE: {device_type}")

        # VM STATUS SET RUNNING/NOT RUNNING
        status = compute_client.virtual_machines.get(resource_group, vm_name, expand='instanceView').instance_view.statuses[1].display_status
        print(f"VM STATE: {status}")

        # USED IN NETWORK INTERFACE SEGMENT
        private_ip = ""
        open_port_list = []

        # NETWORK INTERFACE INFORMATION EXTRACTED
        for interface in vm.network_profile.network_interfaces:

            # NIC REFERENCE INFORMATION
            name = "".join(interface.id.split('/')[-1:])
            sub = "".join(interface.id.split('/')[4])

            # NSG REFERENCE INFORMATION
            nsg = network_client.network_interfaces.get(sub, name).network_security_group
            nsg_name = nsg.id.split('/')[-1]
            nsg_rg_name = nsg.id.split('/')[4]

            # FIND OPEN PORTS
            for rule in network_client.security_rules.list(nsg_rg_name, nsg_name):

                # CHECKS IF NSG RULE IS INBOUND AND TRAFFIC IS ALLOWED
                open_port = (rule.direction == 'Inbound'
                             and rule.access == 'Allow')

                if open_port:
                    # IF PORT IS OPEN IT'S ADDED TO LIST
                    open_port_list.append((rule.name,
                                           rule.destination_port_range))
                    print(f"OPEN : {rule.name}")
                    print(f"PORT : {rule.destination_port_range}")

                else:
                    print(f"PORT NOT OPEN : {rule.name}")  # DEBUG

            # PRIVATE IP ADDRESS
            try:
                # TRIES TO EXTRACT IP CONFIG FROM NIC
                config = network_client.network_interfaces.get(sub, name).ip_configurations

                for x in config:

                    if private_ip == "":
                        private_ip = x.private_ip_address
                        print(f"PRIVATE IP {x.private_ip_address}")

                    else:
                        private_ip = f"{private_ip}, {x.private_ip_address}"
                        print(f"PRIVATE IP {x.private_ip_address}")
            except:
                print("NO IP WAS FOUND")  # DEBUG

        # PUBLIC IP ADDRESS
        # QUERIES LIST OF ALL PUBLIC IP'S IN VM'S RESOURCE GROUP
        public_ips = network_client.public_ip_addresses.list(resource_group)

        # EACH PUBLIC IP IS PROCESSED IN FOR LOOP
        for item in public_ips:
            print(f"NAME : {item.name} ADDR : {item.ip_address}")

            # TRIES TO MATCH IF VM NAME IS CONTAINED IN PUBLIC IP NAME
            if re.match(vm_name, item.name):
                # IF A MATCH IS FOUND PUBLIC IP FOR VM IS SET
                public_ip = item.ip_address

            else:
                pass

        # DICTIONARY OVER VM INFO CREATED
        dic = {
            "host": vm_name,
            "resource_group": resource_group,
            "status": status,
            "os": os,
            "os_type": os_type,
            "device_type": device_type,
            "priviate_ip": private_ip,
            "public_ip": public_ip,
            "open_ports": open_port_list
        }

        # DICTIONARY ADDED TO LIST
        result_list.append(dic)

    # OUTPUT FILED CREATED AND OPENED FOR WRITING
    output = open("cloud-scan.json", "w")
    # RESULT LIST PLACED IN OUTPUT FILE
    json.dump(result_list, output, indent=6)
    # FILE CLOSED
    output.close()
    print(result_list)  # DEBUG
