# Import the needed credential and management objects from the libraries.
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os

#print(f"Provisioning a virtual machine...some operations might take a minute or two.")

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = "xxx"



# Network and IP address names
RESOURCE_GROUP_NAME = "B2S-CloudComp_group"
IP_NAME = "pip1"
LOCATION = "westeurope"
IP_CONFIG_NAME = "python-example-ip-config"


network_client = NetworkManagementClient(credential, subscription_id)



# Step 1: Provision an IP address and wait for completion
poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": { "name": "Standard" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)

ip_address_result = poller.result()

print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

NIC_NAME= "networkInterfaceCard1"

SUBNET_ID = "/subscriptions/xxx/resourceGroups/B2S-CloudComp_group/providers/Microsoft.Network/virtualNetworks/B2S-CloudComp_group-vnet/subnets/default"

# Step 2: Provision the network interface client
poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
    NIC_NAME, 
    {
        "location": LOCATION,
        "ip_configurations": [ {
            "name": IP_CONFIG_NAME,
            "subnet": { "id": SUBNET_ID },
            "public_ip_address": {"id": ip_address_result.id }
        }]
    }
)

nic_result = poller.result()

print(f"Provisioned network interface client {nic_result.name}")

# Step 6: Provision the virtual machine

# Obtain the management object for virtual machines
compute_client = ComputeManagementClient(credential, subscription_id)

VM_NAME = "CloudCompVM2"
USERNAME = "azureuser"
PASSWORD = "password"

print(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")

# Provision the VM specifying only minimal arguments, which defaults to an Ubuntu 18.04 VM
# on a Standard DS1 v2 plan with a public IP address and a default virtual network/subnet.

poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
    {
        "name": "test",
        "location": LOCATION,
        "storage_profile": {
            "image_reference": {
                "publisher": 'Canonical',
                "offer": "UbuntuServer",
                "sku": "16.04.0-LTS",
                "version": "latest"
            }
        },


        "storageProfile": {
            "imageReference": {
            "sku": "16.04-LTS",
            "publisher": "Canonical",
            "version": "latest",
            "offer": "UbuntuServer"
            },
        "dataDisks": []
        },
        "hardware_profile": {
            "vmSize": "Standard_D1_v2"
        },
        "os_profile": {
            "adminUsername": "habeeb",
            "secrets": [
            ],
            "computerName": "myVM",
            "linuxConfiguration": {
                "ssh": {
                "publicKeys": [ 
                    {
                    "path": "/home/habeeb/.ssh/authorized_keys",
                    "keyData": "xxx"
                    }
                ]
                },
            },
            "disablePasswordAuthentication": "true",
            
        },
        "network_profile": {
            "network_interfaces": [{
                "id": nic_result.id,
                "properties": {
                    "primary":"true"
                }
            }]
        }        
    }
)

vm_result = poller.result()

print(f"Provisioned virtual machine {vm_result.name}")
