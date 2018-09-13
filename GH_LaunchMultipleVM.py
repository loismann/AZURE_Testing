import scriptcontext as sc
import time

# These are the original import statements that will not be needed in grasshopper
# from azure.common.credentials import ServicePrincipalCredentials
# from azure.mgmt.resource import ResourceManagementClient
# from azure.mgmt.computeimport ComputeManagementClient
# from azure.mgmt.networkimport NetworkManagementClient
# from azure.mgmt.compute.modelsimport DiskCreateOption

# General Variables
SUBSCRIPTION_ID = '1153c71f-6990-467b-b1ec-c2ba46824d64'
GROUP_NAME = 'AUTOBUNTU'
LOCATION = 'southcentralus'
VM_NAME = 'AutoBuntu'
ADMIN_NAME = "pferrer"
ADMIN_PSWD = "Password_001"


#
############################################### SUPPORTING RESOURCE SETUP ###############################################
#
# This gets all Active Directory credentials
def get_credentials():
    credentials = sc.sticky['azure.common.credentials'].ServicePrincipalCredentials(
        client_id='36783696-531f-4a87-8276-b6e477560a0c',
        secret='2kvy1gZpynDzcluutR+Vw2WE2DcOshPH5u2gVvw/JX0=',
        tenant='0ce7a0d4-9659-4ec3-bda3-9388f55c55af'
    )

    return credentials


# This Creates a resource group
def create_resource_group(resource_group_client):
    resource_group_params = {'location': LOCATION}
    resource_group_result = resource_group_client.resource_groups.create_or_update(
        GROUP_NAME,
        resource_group_params
    )


# This creates an availability set (look more into what these do)
def create_availability_set(compute_client, Instance):
    avset_params = {
        'location': LOCATION,
        'sku': {'name': 'Aligned'},
        'platform_fault_domain_count': 3
    }
    availability_set_result = compute_client.availability_sets.create_or_update(
        GROUP_NAME,
        'myAVSet' + "_" + str(Instance),
        avset_params
    )


# This creates MULTIPLE public IP addresses
def create_public_ip_address(network_client, Instance):
    public_ip_addess_params = {
        'location': LOCATION,
        'public_ip_allocation_method': 'Dynamic'
    }
    creation_result = network_client.public_ip_addresses.create_or_update(
        GROUP_NAME,
        'myIPAddress' + "_" + str(Instance),
        public_ip_addess_params
    )
    return creation_result.result()


# This creates a virtual network
def create_vnet(network_client, Instance):
    vnet_params = {
        'location': LOCATION,
        'address_space': {
            'address_prefixes': ['10.0.0.0/16']
        }
    }
    creation_result = network_client.virtual_networks.create_or_update(
        GROUP_NAME,
        'myVNet' + "_" + str(Instance),
        vnet_params
    )
    while not creation_result.done():
        time.sleep(10)

    return creation_result.result()


# This adds the subnet to the virtual network
def create_subnet(network_client, Instance):
    subnet_params = {
        'address_prefix': '10.0.0.0/24'
    }
    creation_result = network_client.subnets.create_or_update(
        GROUP_NAME,
        'myVNet' + "_" + str(Instance),
        'mySubnet' + "_" + str(Instance),
        subnet_params
    )
    return creation_result.result()


# This creates a network interface for the virtual network
def create_nic(network_client, Instance):
    subnet_info = network_client.subnets.get(
        GROUP_NAME,
        'myVNet' + "_" + str(Instance),
        'mySubnet' + "_" + str(Instance),
    )
    publicIPAddress = network_client.public_ip_addresses.get(
        GROUP_NAME,
        'myIPAddress' + "_" + str(Instance)
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
        'myNic' + "_" + str(Instance),
        nic_params
    )
    while not creation_result.done():
        time.sleep(5)
    return creation_result.result()


# This will create a CUSTOM virtual machine
def create_customvm(network_client, compute_client, Instance):
    nic = network_client.network_interfaces.get(
        GROUP_NAME,
        'myNic' + "_" + str(Instance)
    )
    avset = compute_client.availability_sets.get(
        GROUP_NAME,
        'myAVSet' + "_" + str(Instance)
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
                'id': '/subscriptions/1153c71f-6990-467b-b1ec-c2ba46824d64/resourceGroups/Ubuntu_Radiance_LINE/providers/Microsoft.Compute/images/RadianceTemplate_LINE'
            }
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic.id
            }]
        },
        'availability_set': {
            'id': avset.id
        }
    }
    creation_result = compute_client.virtual_machines.create_or_update(
        GROUP_NAME,
        VM_NAME + "-" + str(Instance),
        vm_parameters
    )
    while not creation_result.done():
        time.sleep(5)

    return creation_result.result()


# Run Code
credentials = get_credentials()

# Initialize Manegement Clients
resource_group_client = sc.sticky['azure.mgmt.resource'].ResourceManagementClient(
    credentials,
    SUBSCRIPTION_ID
)

network_client = sc.sticky['azure.mgmt.network'].NetworkManagementClient(
    credentials,
    SUBSCRIPTION_ID
)

compute_client = sc.sticky['azure.mgmt.compute'].ComputeManagementClient(
    credentials,
    SUBSCRIPTION_ID
)

# Run the VM Creation Loop

if Generate_VM:
    for i in range(int(VM_Count)):
        print("Creating Instance " + str(i))
        # Create an Availability Set
        create_availability_set(compute_client, i)
        print("Availability Set Created")
        # Create a public IP address
        create_public_ip_address(network_client, i)
        print("IP Address Created")
        # Create virtual network
        create_vnet(network_client, i)
        print("Virtual Network Created")
        # Create Subnet
        create_subnet(network_client, i)
        print("Subnet Created")
        # Create Network Interface
        create_nic(network_client, i)
        print("Network Interface Created")
        # Create Custom VM
        create_customvm(network_client, compute_client, i)
        print("VM Created")
        print
        "-----------------------------------------------------------------"


else:
    print("Switch Turned Off")


