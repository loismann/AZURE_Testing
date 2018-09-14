

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption

#General Variables
SUBSCRIPTION_ID = '1153c71f-6990-467b-b1ec-c2ba46824d64'
GROUP_NAME = 'AUTOBUNTU'
LOCATION = 'southcentralus'
VM_NAME = 'AutoBuntu'
ADMIN_NAME = "pferrer"
ADMIN_PSWD = "Password_001"

############################################## SUPPORTING RESOURCE SETUP ###############################################

#This gets all Active Directory credentials
def get_credentials():
    credentials = ServicePrincipalCredentials(
        client_id = '36783696-531f-4a87-8276-b6e477560a0c',
        secret = '2kvy1gZpynDzcluutR+Vw2WE2DcOshPH5u2gVvw/JX0=',
        tenant = '0ce7a0d4-9659-4ec3-bda3-9388f55c55af'
    )

    return credentials

#Run Code
credentials = get_credentials()

# Initialize Management Clients
resource_group_client = ResourceManagementClient(
    credentials,
    SUBSCRIPTION_ID
)

network_client = NetworkManagementClient(
    credentials,
    SUBSCRIPTION_ID
)

compute_client = ComputeManagementClient(
    credentials,
    SUBSCRIPTION_ID
)

#Get the VM Instance
vm = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME, expand='instanceView')

# Unfortunate and convoluted way of obtaining public IP of selected instance
ni_reference = vm.network_profile.network_interfaces[0]
ni_reference = ni_reference.id.split('/')
ni_group = ni_reference[4]
ni_name = ni_reference[8]

net_interface = network_client.network_interfaces.get(ni_group, ni_name)
ip_reference = net_interface.ip_configurations[0].public_ip_address
ip_reference = ip_reference.id.split('/')
ip_group = ip_reference[4]
ip_name = ip_reference[8]

public_ip = network_client.public_ip_addresses.get(ip_group, ip_name)
public_ip = public_ip.ip_address
print(public_ip)