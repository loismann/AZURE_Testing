

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption

from Login_Info import *
import time




############################################## SUPPORTING RESOURCE SETUP ###############################################

#This gets all Active Directory credentials
def get_credentials():
    credentials = ServicePrincipalCredentials(
        client_id = APPLICATION_ID,
        secret = AUTHENTICATION_KEY,
        tenant = DIRECTORY_ID,
    )

    return credentials

# This Creates a resource group
def create_resource_group(resource_group_client):
    resource_group_params = {'location':LOCATION}
    resource_group_result = resource_group_client.resource_groups.create_or_update(
        GROUP_NAME,
        resource_group_params
    )

# This creates an availability set (look more into what these do)
def create_availability_set(compute_client):
    avset_params = {
        'location': LOCATION,
        'sku': { 'name': 'Aligned' },
        'platform_fault_domain_count': 3
    }
    availability_set_result = compute_client.availability_sets.create_or_update(
        GROUP_NAME,
        'myAVSet',
        avset_params
    )


# Reference Existing HKS Network
def ref_private_ip_address(network_client):
    private_ip = network_client.network_interfaces.get('RenderFarmVNET', 'vnettest590').ip_configurations[0].private_ip_address
    print(private_ip)

# This creates a public IP address
def create_public_ip_address(network_client):
    public_ip_addess_params = {
        'location': LOCATION,
        'public_ip_allocation_method': 'Dynamic'
    }
    creation_result = network_client.public_ip_addresses.create_or_update(
        Network_GROUP_NAME,
        'AUTOBUNTU_myIPAddress',
        public_ip_addess_params
    )

    return creation_result.result()

# This will hopefully delete the public IP address
def disassociate_public_ip_address(compute_client, network_client):
    nic = network_client.network_interfaces.get(Network_GROUP_NAME, 'AUTOBUNTU_myNic', )
    #https://docs.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.v2018_08_01.models.networkinterfaceipconfiguration?view=azure-python
    #https://github.com/Azure/azure-sdk-for-python/issues/695#issuecomment-236024219
    # This will dissassocate the public ip address from the VM:
    nic.ip_configurations[0].public_ip_address = None
    # This updates the network interface that currently exists with the properties of the variable "nic" assigned above
    network_client.network_interfaces.create_or_update(Network_GROUP_NAME, 'AUTOBUNTU_myNic', nic)


# This creates a virtual network
def create_vnet(network_client):
    vnet_params = {
        'location': LOCATION,
        'address_space': {
            'address_prefixes': ['10.0.0.0/16']
        }
    }
    creation_result = network_client.virtual_networks.create_or_update(
        GROUP_NAME,
        'myVNet',
        vnet_params
    )
    return creation_result.result()

# This adds the subnet to the virtual network
def create_subnet(network_client):
    subnet_params = {
        'address_prefix': '10.0.0.0/24'
    }
    creation_result = network_client.subnets.create_or_update(
        GROUP_NAME,
        'myVNet',
        'mySubnet',
        subnet_params
    )

    return creation_result.result()

# This creates a network interface (from scratch) for the virtual network
def create_nic(network_client):
    subnet_info = network_client.subnets.get(
        GROUP_NAME,
        'myVNet',
        'mySubnet'
    )
    publicIPAddress = network_client.public_ip_addresses.get(
        GROUP_NAME,
        'myIPAddress'
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
        'myNic',
        nic_params
    )

    return creation_result.result()

# This creates a network interface using Existing HKS Resources
def create_HKSnic(network_client):
    subnet_info = network_client.subnets.get(
        Network_GROUP_NAME,
        Network_VNET,
        Network_SUBNET
    )
    publicIPAddress = network_client.public_ip_addresses.get(
        Network_GROUP_NAME,
        'AUTOBUNTU_myIPAddress'
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
        Network_GROUP_NAME,
        'AUTOBUNTU_myNic',
        nic_params
    )

    return creation_result.result()


########################################### VIRTUAL MACHINE SETUP AND USE ##############################################



# This will create a virtual machine
def create_vm(network_client, compute_client):
    nic = network_client.network_interfaces.get(
        Network_GROUP_NAME,
        'AUTOBUNTU_myNic'
    )
    # avset = compute_client.availability_sets.get(
    #     GROUP_NAME,
    #     'myAVSet'
    # )
    vm_parameters = {
        'location': LOCATION,
        'os_profile': {
            'computer_name': VM_NAME,
            'admin_username': ADMIN_NAME,
            'admin_password': ADMIN_PSWD
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1'
        },
        'storage_profile': {
            'image_reference': {
                'publisher': 'Canonical',
                'offer': 'UbuntuServer',
                'sku': '16.04-LTS',
                'version': 'latest'
            }
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic.id
            }]
        },
        # 'availability_set': {
        #     'id': avset.id
        # }
    }
    creation_result = compute_client.virtual_machines.create_or_update(
        GROUP_NAME,
        VM_NAME,
        vm_parameters
    )

    return creation_result.result()

# This will create a CUSTOM virtual machine
def create_customvm(network_client, compute_client):
    nic = network_client.network_interfaces.get(
        GROUP_NAME,
        'myNic'
    )
    # avset = compute_client.availability_sets.get(
    #     GROUP_NAME,
    #     'myAVSet'
    # )
    vm_parameters = {
        'location': LOCATION,
        'os_profile': {
            'computer_name': VM_NAME,
            'admin_username': ADMIN_NAME,
            'admin_password': ADMIN_PSWD
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1'
        },
        'storage_profile': {
            'image_reference': {
                'id' : '/subscriptions/1153c71f-6990-467b-b1ec-c2ba46824d64/resourceGroups/Ubuntu_Radiance_LINE/providers/Microsoft.Compute/images/RadianceTemplate_LINE'
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
        VM_NAME,
        vm_parameters
    )

    return creation_result.result()

# This will give information about the current VM
def get_vm(compute_client):
    vm = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME, expand='instanceView')
    print("hardwareProfile")
    print("   vmSize: ", vm.hardware_profile.vm_size)
    print("\nstorageProfile")
    print("  imageReference")
    print("    publisher: ", vm.storage_profile.image_reference.publisher)
    print("    offer: ", vm.storage_profile.image_reference.offer)
    print("    sku: ", vm.storage_profile.image_reference.sku)
    print("    version: ", vm.storage_profile.image_reference.version)
    print("  osDisk")
    print("    osType: ", vm.storage_profile.os_disk.os_type.value)
    print("    name: ", vm.storage_profile.os_disk.name)
    print("    createOption: ", vm.storage_profile.os_disk.create_option.value)
    print("    caching: ", vm.storage_profile.os_disk.caching.value)
    print("\nosProfile")
    print("  computerName: ", vm.os_profile.computer_name)
    print("  adminUsername: ", vm.os_profile.admin_username)
    #print("  provisionVMAgent: {0}".format(vm.os_profile.windows_configuration.provision_vm_agent))
    #print("  enableAutomaticUpdates: {0}".format(vm.os_profile.windows_configuration.enable_automatic_updates))
    print("\nnetworkProfile")
    for nic in vm.network_profile.network_interfaces:
        print("  networkInterface id: ", nic.id)
    print("\nvmAgent")
    print("  vmAgentVersion", vm.instance_view.vm_agent.vm_agent_version)
    print("    statuses")
    # for stat in vm_result.instance_view.vm_agent.statuses:
    #     print("    code: ", stat.code)
    #     print("    displayStatus: ", stat.display_status)
    #     print("    message: ", stat.message)
    #     print("    time: ", stat.time)
    print("\ndisks");
    for disk in vm.instance_view.disks:
        print("  name: ", disk.name)
        print("  statuses")
        for stat in disk.statuses:
            print("    code: ", stat.code)
            print("    displayStatus: ", stat.display_status)
            print("    time: ", stat.time)
    print("\nVM general status")
    print("  provisioningStatus: ", vm.provisioning_state)
    print("  id: ", vm.id)
    print("  name: ", vm.name)
    print("  type: ", vm.type)
    print("  location: ", vm.location)
    print("\nVM instance status")
    for stat in vm.instance_view.statuses:
        print("  code: ", stat.code)
        print("  displayStatus: ", stat.display_status)

# This will stop the VM
def stop_vm(compute_client):
    compute_client.virtual_machines.power_off(GROUP_NAME, VM_NAME)

# This will deallocate the VM
def deallocate_vm(compute_client):
    compute_client.virtual_machines.deallocate(GROUP_NAME, VM_NAME)

# This will start the virtual machine up (again)
def start_vm(compute_client):
    compute_client.virtual_machines.start(GROUP_NAME, VM_NAME)

# This will resize the virtual machine
def update_vm(compute_client):
    vm = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME)
    vm.hardware_profile.vm_size = 'Standard_DS3'
    update_result = compute_client.virtual_machines.create_or_update(
        GROUP_NAME,
        VM_NAME,
        vm
    )

    return update_result.result()

# This will add another Data disk to the virtual machine
def add_datadisk(compute_client):
    disk_creation = compute_client.disks.create_or_update(
        GROUP_NAME,
        'myDataDisk1',
        {
            'location': LOCATION,
            'disk_size_gb': 1,
            'creation_data': {
                'create_option': DiskCreateOption.empty
            }
        }
    )
    data_disk = disk_creation.result()
    vm = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME)
    add_result = vm.storage_profile.data_disks.append({
        'lun': 1,
        'name': 'myDataDisk1',
        'create_option': DiskCreateOption.attach,
        'managed_disk': {
            'id': data_disk.id
        }
    })
    add_result = compute_client.virtual_machines.create_or_update(
        GROUP_NAME,
        VM_NAME,
        vm)

    return add_result.result()

# This will delete all resources
def delete_resources(resource_group_client):
    resource_group_client.resource_groups.delete(GROUP_NAME)



########################################### RUN VIRTUAL MACHINE CODE ###################################################

Run_Code = True


#Run Code
if __name__ == "__main__" and Run_Code:
    # print("Hello World")
    credentials = get_credentials()
    # print(credentials)
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

    # Call the resource group
    # create_resource_group(resource_group_client)
    # print("Created Resource Group")
    # # Create the availability set
    # create_availability_set(compute_client)
    # print("Created Availability Set")

    # Create a public IP address
    # create_public_ip_address(network_client)

    # Ref private ip
    # print(ref_private_ip_address(network_client))

    # # Create the virtual network
    # create_vnet(network_client)
    # print("Virtual Network Created")

    # # Add the subnet to the virtual network
    # create_subnet(network_client)
    # print("Subnet added to virtual network")

    # Create the network interface
    # create_HKSnic(network_client)
    # print("Network Interface Created")

    # FINALLY Create the virtual machine
    # create_vm(network_client, compute_client)
    # print("Virtual Machine Created")

    # Test the deletion of the public ip
    # sleep first
    # for i in range(25):
    #     print(i)
    #     time.sleep(1)

    result = disassociate_public_ip_address(compute_client, network_client)

    # print("Public IP address removed")
    # Revel in your Success
    # print("Success!!!")

    ## Get information about the VM
    # get_vm(compute_client)
    # print("------------------------------------------------------")
    # input('Info Displayed. Press enter to continue...')

    ## Stop the VM
    # stop_vm(compute_client)
    # input('VM Stopped. Press enter to continue...')

    # Deallocate the VM
    # deallocate_vm(compute_client)
    # input('VM Deallocated.  Press enter to continue...')

    ## Start the VM back up again
    # start_vm(compute_client)
    # input('VM up and running again, Press enter to continue')

    ## Resize the VM
    # update_result = update_vm(compute_client)
    # print("------------------------------------------------------")
    # print(update_result)
    # input('VM has been resized. Press enter to continue...')

    ## Add Data Disk to VM
    # add_result = add_datadisk(compute_client)
    # print("------------------------------------------------------")
    # print(add_result)
    # input('Press enter to continue...')

    ## Deallocate the VM
    # deallocate_vm(compute_client)
    # input('VM Deallocated.  Press enter to continue...')

    ## Delete all resources
    # delete_resources(resource_group_client)
    # input('Resources Deleted. Press enter to continue...')

    # print ("Revel in your success!")
else:
    print ("Just testing stuff")
    print (SUBSCRIPTION_ID)







