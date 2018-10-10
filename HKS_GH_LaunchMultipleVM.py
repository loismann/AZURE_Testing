import scriptcontext as sc
import time
import getpass
import datetime
import Grasshopper.DataTree as DataTree
from Grasshopper.Kernel.Data import GH_Path


#### This sticky dictionary is being used to ensure the log output does not get deleted after boolean button press
if clear_logs:
    if "Message" in sc.sticky != "Nothing Run Yet":
        sc.sticky["Message"] = "Nothing Run Yet"
    if "Global_VM_Count" in sc.sticky:
        sc.sticky["Global_VM_Count"] = None

if sc.sticky.has_key("Message"):
    stickyval = sc.sticky["Message"]

else:
    stickyval = "Nothing Run Yet"


#Add the "VM_Count" Variable to the sticky Dictionary
sc.sticky["Global_VM_Count"] = VM_Count



# General Variables
# These are referenced in from the Login Info File



#
############################################### SUPPORTING RESOURCE SETUP ###############################################
#
# This gets all Active Directory credentials
def get_credentials():
    credentials = sc.sticky['azure.common.credentials'].ServicePrincipalCredentials(
        client_id=sc.sticky['Login_Info'].APPLICATION_ID,
        secret=sc.sticky['Login_Info'].AUTHENTICATION_KEY,
        tenant=sc.sticky['Login_Info'].DIRECTORY_ID,
    )

    return credentials


# This Creates a resource group
def create_resource_group(resource_group_client):
    resource_group_params = {'location': sc.sticky['Login_Info'].LOCATION}
    resource_group_result = resource_group_client.resource_groups.create_or_update(
        sc.sticky['Login_Info'].GROUP_NAME,
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


# This creates a public IP address
def create_public_ip_address(network_client, Instance):
    public_ip_addess_params = {
        'location': sc.sticky['Login_Info'].LOCATION,
        'public_ip_allocation_method': 'Dynamic'
    }
    creation_result = network_client.public_ip_addresses.create_or_update(
        sc.sticky['Login_Info'].GROUP_NAME,
        sc.sticky['Login_Info'].GROUP_NAME + '_IPAddress_' + str(Instance),
        public_ip_addess_params
    )
    return creation_result.result()

# This will disassociate the public IP address from the VM after its created
def disassociate_public_ip_address(compute_client, network_client, Instance):
    nic = network_client.network_interfaces.get(Network_GROUP_NAME, 'AUTOBUNTU_myNic', )
    #https://docs.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.v2018_08_01.models.networkinterfaceipconfiguration?view=azure-python
    #https://github.com/Azure/azure-sdk-for-python/issues/695#issuecomment-236024219
    # This will dissassocate the public ip address from the VM:
    nic.ip_configurations[0].public_ip_address = None
    # This updates the network interface that currently exists with the properties of the variable "nic" assigned above
    network_client.network_interfaces.create_or_update(Network_GROUP_NAME, 'AUTOBUNTU_myNic', nic)


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


# This creates a network interface using Existing HKS Resources
def create_HKSnic(network_client, Instance):
    subnet_info = network_client.subnets.get(
        sc.sticky['Login_Info'].Network_GROUP_NAME,
        sc.sticky['Login_Info'].Network_VNET,
        sc.sticky['Login_Info'].Network_SUBNET
    )
    publicIPAddress = network_client.public_ip_addresses.get(
        sc.sticky['Login_Info'].GROUP_NAME,
        sc.sticky['Login_Info'].GROUP_NAME + '_IPAddress_' + str(Instance),
    )
    nic_params = {
        'location': sc.sticky['Login_Info'].LOCATION,
        'ip_configurations': [{
            'name': 'myIPConfig',
            'public_ip_address': publicIPAddress,
            'subnet': {
                'id': subnet_info.id
            }
        }]
    }
    creation_result = network_client.network_interfaces.create_or_update(
        sc.sticky['Login_Info'].GROUP_NAME,
        sc.sticky['Login_Info'].GROUP_NAME + '_myNic_' + str(Instance),
        nic_params
    )
    while not creation_result.done():
        time.sleep(5)

    return creation_result.result()


# This will create a CUSTOM virtual machine
def create_customvm(network_client, compute_client, Instance):
    nic = network_client.network_interfaces.get(
        sc.sticky['Login_Info'].GROUP_NAME,
        sc.sticky['Login_Info'].GROUP_NAME + '_myNic_' + str(Instance),
    )

    vm_parameters = {
        'location': sc.sticky['Login_Info'].LOCATION,
        'os_profile': {
            'computer_name': sc.sticky['Login_Info'].VM_NAME + "-" + str(Instance),
            'admin_username': sc.sticky['Login_Info'].ADMIN_NAME,
            'admin_password': sc.sticky['Login_Info'].ADMIN_PSWD
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1'
        },
        'storage_profile': {
            'image_reference': {
                'id': '/subscriptions/9fe06a7b-b34d-4fe5-aea4-9c012830c497/resourceGroups/LINE_DISKIMAGES/providers/Microsoft.Compute/images/LINEUbuntuRadianceImage'
            }
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic.id
            }]
        },
    }
    creation_result = compute_client.virtual_machines.create_or_update(
        sc.sticky['Login_Info'].GROUP_NAME,
        sc.sticky['Login_Info'].VM_NAME + "-" + str(Instance),
        vm_parameters
    )
    while not creation_result.done():
        time.sleep(5)

    return creation_result.result()




# # Run Code
credentials = get_credentials()
#
# Initialize Management Clients
resource_group_client = sc.sticky['azure.mgmt.resource'].ResourceManagementClient(
    credentials,
    sc.sticky['Login_Info'].SUBSCRIPTION_ID
)

network_client = sc.sticky['azure.mgmt.network'].NetworkManagementClient(
    credentials,
    sc.sticky['Login_Info'].SUBSCRIPTION_ID
)

compute_client = sc.sticky['azure.mgmt.compute'].ComputeManagementClient(
    credentials,
    sc.sticky['Login_Info'].SUBSCRIPTION_ID
)

# # Create tree structure to pass through the IP Addresses
# T_IPAddress = DataTree[str]()
# Public_IP_List = []

# Run the VM Creation Loop
if Generate_VM:

    # updatecounter = 0
    # # statusbar.ShowProgressMeter(0, ((7*VM_Count)+1), "Calculating", True, True)
    #
    # # Start the sticky dictionary entry
    log_message = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + str("\n")
    #
    # # Create the resource group
    # create_resource_group(resource_group_client)
    # log_message += "Created Resource Group\n\n"
    # # statusbar.UpdateProgressMeter(updatecounter + 1, True)
    # updatecounter += 1
    #
    # for i in range(int(VM_Count)):
    #     path = GH_Path(i)
    #     log_message += "Creating Instance " + str(i) + " ...\n"
    #     # statusbar.UpdateProgressMeter(updatecounter +1 , True)
    #     updatecounter += 1
    #     # Create a public IP address
    #     create_public_ip_address(network_client, i)
    #     log_message += "IP Address Created\n"
    #     # statusbar.UpdateProgressMeter(updatecounter + 1, True)
    #     updatecounter += 1
    #     # Create Network Interface
    #     create_HKSnic(network_client, i)
    #     log_message += "Network Interface Created\n"
    #     # statusbar.UpdateProgressMeter(updatecounter + 1, True)
    #     updatecounter += 1
    #     # Create Custom VM
    #     create_customvm(network_client, compute_client, i)
    #     log_message += "VM Created\n"
    #     log_message += "-----------------------------------------------------------------"
    #     # # statusbar.UpdateProgressMeter(updatecounter + 1, True)
    #
    # # statusbar.HideProgressMeter()
    sc.sticky["Message"] = log_message

    print(stickyval)
    print(log_message)

else:
    print(stickyval)




