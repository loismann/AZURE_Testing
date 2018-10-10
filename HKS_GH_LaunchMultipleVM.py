import scriptcontext as sc
import time
import datetime
import Grasshopper.DataTree as DataTree
from Grasshopper.Kernel.Data import GH_Path
scp = sc.sticky['scp']
paramiko = sc.sticky['paramiko']
client = sc.sticky['paramiko.client']
threading = sc.sticky['threading']


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
def disassociate_public_ip_address(network_client, Instance):
    nic = network_client.network_interfaces.get(sc.sticky['Login_Info'].GROUP_NAME,
                                                sc.sticky['Login_Info'].GROUP_NAME + '_myNic_' + str(Instance), )
    #https://docs.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.v2018_08_01.models.networkinterfaceipconfiguration?view=azure-python
    #https://github.com/Azure/azure-sdk-for-python/issues/695#issuecomment-236024219
    # This will dissassocate the public ip address from the VM:
    nic.ip_configurations[0].public_ip_address = None
    # This updates the network interface that currently exists with the properties of the variable "nic" assigned above
    network_client.network_interfaces.create_or_update(sc.sticky['Login_Info'].GROUP_NAME,
                                                       sc.sticky['Login_Info'].GROUP_NAME + '_myNic_' + str(Instance),
                                                       nic)

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

# This will find the private (internal HKS) IP address for a VM
def getPrivateIpAddress(network_client, Instance):
    nic = network_client.network_interfaces.get(sc.sticky['Login_Info'].GROUP_NAME,
                                                sc.sticky['Login_Info'].GROUP_NAME + '_myNic_' + str(Instance), )
    #https://docs.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.v2018_08_01.models.networkinterfaceipconfiguration?view=azure-python
    #https://github.com/Azure/azure-sdk-for-python/issues/695#issuecomment-236024219
    # This will dissassocate the public ip address from the VM:
    privateIP = nic.ip_configurations[0].private_ip_address
    # This updates the network interface that currently exists with the properties of the variable "nic" assigned above
    network_client.network_interfaces.create_or_update(sc.sticky['Login_Info'].GROUP_NAME,
                                                       sc.sticky['Login_Info'].GROUP_NAME + '_myNic_' + str(Instance),
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
    # log_message = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #
    # # Create the resource group
    # create_resource_group(resource_group_client)
    # log_message += "\nCreated Resource Group\n\n"
    # # statusbar.UpdateProgressMeter(updatecounter + 1, True)
    # updatecounter += 1

    for i in range(int(VM_Count)):
        # path = GH_Path(i)
        # log_message += "Creating Instance " + str(i) + " ...\n"
        # # statusbar.UpdateProgressMeter(updatecounter +1 , True)
        # updatecounter += 1
        # # Create a public IP address
        # create_public_ip_address(network_client, i)
        # log_message += "IP Address Created\n"
        # # statusbar.UpdateProgressMeter(updatecounter + 1, True)
        # updatecounter += 1
        # # Create Network Interface
        # create_HKSnic(network_client, i)
        # log_message += "Network Interface Created\n"
        # # statusbar.UpdateProgressMeter(updatecounter + 1, True)
        # updatecounter += 1
        # # Create Custom VM
        # create_customvm(network_client, compute_client, i)
        # log_message += "VM Created\n"
        # # Disassociate the IP address from the VM
        # disassociate_public_ip_address(network_client, i)
        # log_message += "Public IP address unlinked"
        # log_message += "--------------------------------------------\n"
        # # # statusbar.UpdateProgressMeter(updatecounter + 1, True)



        # Get the private IP address of the newly created VM
        private_IP = getPrivateIpAddress(network_client,i)
        # Connect to the newly created VM
        connection = ssh(private_IP,
                         sc.sticky['Login_Info'].ADMIN_NAME,
                         sc.sticky['Login_Info'].ADMIN_PSWD,
                         )
        # Update the Radiance Path entries
        connection.sendCommand(r"sed -i -e '$a\' -e '' /home/pferrer/.bashrc")
        connection.sendCommand(r"sed -i -e '$a\' -e 'RAYPATH=.:/usr/local/lib/:$RAYPATH' /home/pferrer/.bashrc")
        connection.sendCommand(r"sed -i -e '$a\' -e 'PATH=.:/usr/local/bin/:$PATH' /home/pferrer/.bashrc")
        connection.sendCommand(r"sed -i -e '$a\' -e 'MANPATH=.:/home/pferrer/ray/doc/man/:$MANPATH' /home/pferrer/.bashrc")
        connection.sendCommand(r"sed -i -e '$a\' -e 'export PATH RAYPATH MANPATH' /home/pferrer/.bashrc")


    # statusbar.HideProgressMeter()
    sc.sticky["Message"] = log_message

    print(stickyval)
    # print(log_message)

else:
    print(stickyval)




