import time
import datetime
from paramiko import client
from HELPER_Login_Info import *
from HELPER_SMS import SMS
import HELPER_Management_Clients



############################################### SUPPORTING RESOURCE SETUP ###############################################


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

# This will disassociate the public IP address from the VM after its created
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

# This creates a network interface using Existing HKS Resources
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

# This will create a CUSTOM virtual machine
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

# This Class governs connections to the VM so commands can be run
class ssh:
    client = None

    def __init__(self, address, username, password):
        # Let the user know we're connecting to the server
        print("Connecting to server...")
        # Create a new SSH client
        self.client = client.SSHClient()
        # The following line is required if you want to script to be able to access a server thats not yet in the known_hosts file
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        # Make the connection
        self.client.connect(address,username=username,password=password,look_for_keys=False)

    def sendCommand(self,command):
        # Check to see if connection has been made previously
        if(self.client):
            stdin,stdout,stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print stdout data when available
                if stdout.channel.recv_ready():
                    # Retrieve the first 1024 bytes
                    alldata = stdout.channel.recv(1024)
                    while stdout.channel.recv_ready():
                        # Retrieve the next 1024 bytes
                        alldata += stdout.channel.recv(1024)

                    # Print as string with utf8 encoding
                    print(str(alldata, "utf8"))
        else:
            print("Connection not opened.")

# This will add the missing path entries to the newly created vm
def updateRadiancePathEntries(Instance):
    pass



# # Run Code

# Initialize Management Clients
mgmt = HELPER_Management_Clients.MGMT()
# Instantiate the SMS class
sms = SMS()


# Run the VM Creation Loop
Generate_VM = True
VM_Count = 4
if Generate_VM:


    # Start the sticky dictionary entry
    log_message = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create the resource group
    create_resource_group(mgmt.resource_group_client())
    log_message += "\nCreated Resource Group\n\n"

    for i in range(int(VM_Count)):
        log_message += "Creating Instance " + str(i) + " ...\n"
        print("Creating Instance " + str(i) + " ...")

        # Create a public IP address
        create_public_ip_address(mgmt.network_client(), i)
        log_message += "IP Address Created\n"
        print("IP Address Created")

        # Create Network Interface
        create_HKSnic(mgmt.network_client(), i)
        log_message += "Network Interface Created\n"
        print("Network Interface Created")

        # Create Custom VM
        create_customvm(mgmt.network_client(), mgmt.compute_client(), i)
        log_message += "VM Created\n"
        print("VM " + str(i) + " Created")
        sms.CreateVM(i)

        # Disassociate the IP address from the VM
        disassociate_public_ip_address(mgmt.network_client(), i)
        log_message += "Public IP address unlinked"
        log_message += "--------------------------------------------\n"
        print("Public IP address unlinked\n----------------------------------------\n")
        # # statusbar.UpdateProgressMeter(updatecounter + 1, True)



        # Get the private IP address of the newly created VM
        # private_IP = getPrivateIpAddress(network_client,i)
        # # Connect to the newly created VM
        # connection = ssh(private_IP,
        #                  sc.sticky['Login_Info'].ADMIN_NAME,
        #                  sc.sticky['Login_Info'].ADMIN_PSWD,
        #                  )


else:
    print("Just Testing Stuff")