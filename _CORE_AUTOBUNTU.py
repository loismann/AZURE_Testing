import time


################# These are all the functions that will be used in the Autobuntu project #######################

# This Creates a resource group
def create_resource_group(resource_group_client,Login_Class):
    resource_group_params = {'location':Login_Class.LOCATION}
    resource_group_result = resource_group_client.resource_groups.create_or_update(
        Login_Class.GROUP_NAME,
        resource_group_params
    )

# This creates a public IP address
def create_public_ip_address(network_client, Instance, Login_Class):
    public_ip_addess_params = {
        'location': Login_Class.LOCATION,
        'public_ip_allocation_method': 'Dynamic'
    }
    creation_result = network_client.public_ip_addresses.create_or_update(
        Login_Class.GROUP_NAME,
        Login_Class.GROUP_NAME + '_IPAddress_' + str(Instance),
        public_ip_addess_params
    )

    while not creation_result.done():
        time.sleep(5)

    return creation_result.result()

# This  disassociates the public IP address from the VM after its created
def disassociate_public_ip_address(network_client, Instance,Login_Class):
    nic = network_client.network_interfaces.get(Login_Class.GROUP_NAME,
                                                Login_Class.GROUP_NAME + '_myNic_' + str(Instance), )
    #https://docs.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.v2018_08_01.models.networkinterfaceipconfiguration?view=azure-python
    #https://github.com/Azure/azure-sdk-for-python/issues/695#issuecomment-236024219
    # This will dissassocate the public ip address from the VM:
    nic.ip_configurations[0].public_ip_address = None
    # This updates the network interface that currently exists with the properties of the variable "nic" assigned above
    network_client.network_interfaces.create_or_update(Login_Class.GROUP_NAME,
                                                       Login_Class.GROUP_NAME + '_myNic_' + str(Instance),
                                                       nic)

# This creates a network interface using EXISTING HKS Resources
def create_HKSnic(network_client, Instance,Login_Class):
    subnet_info = network_client.subnets.get(
        Login_Class.Network_GROUP_NAME,
        Login_Class.Network_VNET,
        Login_Class.Network_SUBNET
    )
    publicIPAddress = network_client.public_ip_addresses.get(
        Login_Class.GROUP_NAME,
        Login_Class.GROUP_NAME + '_IPAddress_' + str(Instance),
    )
    nic_params = {
        'location': Login_Class.LOCATION,
        'ip_configurations': [{
            'name': 'myIPConfig',
            'public_ip_address': publicIPAddress,
            'subnet': {
                'id': subnet_info.id
            }
        }]
    }
    creation_result = network_client.network_interfaces.create_or_update(
        Login_Class.GROUP_NAME,
        Login_Class.GROUP_NAME + '_myNic_' + str(Instance),
        nic_params
    )
    print("Creating NIC...")
    while not creation_result.done():
        time.sleep(5)

    return creation_result.result()

# This will create a CUSTOM virtual machine from an HKS specific Radiance image
def create_customvm(network_client, compute_client, Instance, Login_Class):
    nic = network_client.network_interfaces.get(
        Login_Class.GROUP_NAME,
        Login_Class.GROUP_NAME + '_myNic_' + str(Instance),
    )

    vm_parameters = {
        'location': Login_Class.LOCATION,
        'os_profile': {
            'computer_name': Login_Class.VM_NAME + "-" + str(Instance),
            'admin_username': Login_Class.ADMIN_NAME,
            'admin_password': Login_Class.ADMIN_PSWD
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
        Login_Class.GROUP_NAME,
        Login_Class.VM_NAME + "-" + str(Instance),
        vm_parameters
    )
    print("creating VM...")
    while not creation_result.done():
        time.sleep(5)

    return creation_result.result()

# This will find the private (internal HKS) IP address for a VM
def getPrivateIpAddress(network_client, Instance,Login_Class):
    nic = network_client.network_interfaces.get(Login_Class.GROUP_NAME,
                                                Login_Class.GROUP_NAME + '_myNic_' + str(Instance), )
    #https://docs.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.v2018_08_01.models.networkinterfaceipconfiguration?view=azure-python
    #https://github.com/Azure/azure-sdk-for-python/issues/695#issuecomment-236024219
    # This will disassocate the public ip address from the VM:
    privateIP = nic.ip_configurations[0].private_ip_address
    # This updates the network interface that currently exists with the properties of the variable "nic" assigned above
    network_client.network_interfaces.create_or_update(Login_Class.GROUP_NAME,
                                                       Login_Class.GROUP_NAME + '_myNic_' + str(Instance),
                                                       nic)
    return privateIP

# This will add the missing path entries to the newly created vm - Probably not needed as radiance is now installed
# outside of the home directory
def updateRadiancePathEntries(Instance):
    pass

#Delete All the Resources
def delete_resources(resource_group_client,Login_Class):
    creation_result = resource_group_client.resource_groups.delete(Login_Class.GROUP_NAME)
    print("Deleting Resources...")
    while not creation_result.done():
        time.sleep(10)


################# These are generic, related functions not currently being used ########################################

# NOTE: These functions were pulled straight from a tutorial and have not been modified to work with AutoBuntu.
# NOTE: Instance and Login_Class arguments need to be referenced into the functions before use

# This creates an availability set (look more into what these do)
def create_availability_set(compute_client, Instance,Login_Class):
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

# This creates a virtual network
def create_vnet(network_client, Instance,Login_Class):
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
def create_subnet(network_client, Instance,Login_Class):
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

# This creates a network interface for the virtual network
def create_nic(network_client, Instance,Login_Class):
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

# This will create a virtual machine from an Azure Marketplace template
def create_vm(network_client, compute_client, Instance,Login_Class):
    nic = network_client.network_interfaces.get(
        GROUP_NAME,
        'myNic'
    )
    avset = compute_client.availability_sets.get(
        GROUP_NAME,
        'myAVSet'
    )
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
def get_vm(compute_client, Instance,Login_Class):
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
def stop_vm(compute_client, Instance,Login_Class):
    compute_client.virtual_machines.power_off(GROUP_NAME, VM_NAME)

# This will deallocate the VM
def deallocate_vm(compute_client, Instance,Login_Class):
    compute_client.virtual_machines.deallocate(GROUP_NAME, VM_NAME)

# This will start the virtual machine up (again)
def start_vm(compute_client, Instance,Login_Class):
    compute_client.virtual_machines.start(GROUP_NAME, VM_NAME)

# This will resize the virtual machine
def update_vm(compute_client, Instance,Login_Class):
    vm = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME)
    vm.hardware_profile.vm_size = 'Standard_DS3'
    update_result = compute_client.virtual_machines.create_or_update(
        GROUP_NAME,
        VM_NAME,
        vm
    )

    return update_result.result()

# This will add another Data disk to the virtual machine (but will not mount it. that is a separate process)
def add_datadisk(compute_client, Instance,Login_Class):
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


####################################### WORK IN PROGRESS ##########################################################

# This will get the public IP address of a series of VM's
#Get the VM Instance
def get_vmPublicIP():
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