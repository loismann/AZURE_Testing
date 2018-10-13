import time
import datetime
from paramiko import client
from HELPERS.HELPER_Login_Info import *


# These are all the functions that will be used in the Autobuntu project

# This Creates a resource group
def create_resource_group(resource_group_client):
    resource_group_params = {'location':LOCATION}
    resource_group_result = resource_group_client.resource_groups.create_or_update(
        GROUP_NAME,
        resource_group_params
    )

# This creates a public IP address
def create_public_ip_address(network_client, Instance):
    public_ip_addess_params = {
        'location': LOCATION,
        'public_ip_allocation_method': 'Dynamic'
    }
    creation_result = network_client.public_ip_addresses.create_or_update(
        GROUP_NAME,
        GROUP_NAME + '_IPAddress_' + str(Instance),
        public_ip_addess_params
    )

    while not creation_result.done():
        time.sleep(5)

    return creation_result.result()

# This  disassociates the public IP address from the VM after its created
def disassociate_public_ip_address(network_client, Instance):
    nic = network_client.network_interfaces.get(GROUP_NAME,
                                                GROUP_NAME + '_myNic_' + str(Instance), )
    #https://docs.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.v2018_08_01.models.networkinterfaceipconfiguration?view=azure-python
    #https://github.com/Azure/azure-sdk-for-python/issues/695#issuecomment-236024219
    # This will dissassocate the public ip address from the VM:
    nic.ip_configurations[0].public_ip_address = None
    # This updates the network interface that currently exists with the properties of the variable "nic" assigned above
    network_client.network_interfaces.create_or_update(GROUP_NAME,
                                                       GROUP_NAME + '_myNic_' + str(Instance),
                                                       nic)

# This creates a network interface using EXISTING HKS Resources
def create_HKSnic(network_client, Instance):
    subnet_info = network_client.subnets.get(
        Network_GROUP_NAME,
        Network_VNET,
        Network_SUBNET
    )
    publicIPAddress = network_client.public_ip_addresses.get(
        GROUP_NAME,
        GROUP_NAME + '_IPAddress_' + str(Instance),
    )
    nic_params = {
        'location': LOCATION,
        'ip_configurations': [{
            'name': 'myIPConfig',
            'public_ip_address': publicIPAddress,
            'subnet': {
                'id': subnet_info.id
            }
        }]
    }
    creation_result = network_client.network_interfaces.create_or_update(
        GROUP_NAME,
        GROUP_NAME + '_myNic_' + str(Instance),
        nic_params
    )
    while not creation_result.done():
        print("Creating NIC...")
        time.sleep(5)

    return creation_result.result()

# This will create a CUSTOM virtual machine from an HKS specific Radiance image
def create_customvm(network_client, compute_client, Instance):
    nic = network_client.network_interfaces.get(
        GROUP_NAME,
        GROUP_NAME + '_myNic_' + str(Instance),
    )

    vm_parameters = {
        'location': LOCATION,
        'os_profile': {
            'computer_name': VM_NAME + "-" + str(Instance),
            'admin_username': ADMIN_NAME,
            'admin_password': ADMIN_PSWD
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1'
        },
        'storage_profile': {
            'image_reference': {
                'id': '/subscriptions/9fe06a7b-b34d-4fe5-aea4-9c012830c497/resourceGroups/LINE_DISKIMAGES/providers/Microsoft.Compute/images/LINE_RADIANCE_IMAGE'
            }
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic.id
            }]
        },
    }
    creation_result = compute_client.virtual_machines.create_or_update(
        GROUP_NAME,
        VM_NAME + "-" + str(Instance),
        vm_parameters
    )
    while not creation_result.done():
        print("creating VM...")
        time.sleep(5)

    return creation_result.result()

# This will find the private (internal HKS) IP address for a VM
def getPrivateIpAddress(network_client, Instance):
    nic = network_client.network_interfaces.get(GROUP_NAME,
                                                GROUP_NAME + '_myNic_' + str(Instance), )
    #https://docs.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.v2018_08_01.models.networkinterfaceipconfiguration?view=azure-python
    #https://github.com/Azure/azure-sdk-for-python/issues/695#issuecomment-236024219
    # This will dissassocate the public ip address from the VM:
    privateIP = nic.ip_configurations[0].private_ip_address
    # This updates the network interface that currently exists with the properties of the variable "nic" assigned above
    network_client.network_interfaces.create_or_update(GROUP_NAME,
                                                       GROUP_NAME + '_myNic_' + str(Instance),
                                                       nic)
    return privateIP

# This will add the missing path entries to the newly created vm
def updateRadiancePathEntries(Instance):
    pass


print(GROUP_NAME)