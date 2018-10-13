import time
import datetime
from paramiko import client
from HELPERS.HELPER_Login_Info import *
from HELPERS.HELPER_SMS import SMS
import HELPERS.HELPER_Management_Clients
import _CORE_AUTOBUNTU as core
import os




##########################################   Run Code   ################################################################

# Initialize Management Clients
mgmt = HELPERS.HELPER_Management_Clients.MGMT()
# Instantiate the SMS class
sms = SMS()


# Run the VM Creation Loop
Generate_VM = True
VM_Count = 2
if Generate_VM:


    # Start the sticky dictionary entry
    log_message = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create the resource group
    core.create_resource_group(mgmt.resource_group_client())
    log_message += "\nCreated Resource Group\n\n"

    # Create (or override) an empty file to hold the Local IP addresses when this is done

    IP_File = open(os.path.join(os.getcwd(), 'HELPERS', 'Local_IP_Addresses.py'), 'w')


    for i in range(int(VM_Count)):
        log_message += "Creating Instance " + str(i) + " ...\n"
        print("Creating Instance " + str(i) + " ...")

        # Create a public IP address
        core.create_public_ip_address(mgmt.network_client(), i)
        log_message += "IP Address Created\n"
        print("IP Address Created")


        # Create Network Interface
        core.create_HKSnic(mgmt.network_client(), i)
        log_message += "Network Interface Created\n"
        print("Network Interface Created")

        # Create Custom VM
        core.create_customvm(mgmt.network_client(), mgmt.compute_client(), i)
        log_message += "VM Created\n"
        print("VM " + str(i) + " Created")
        sms.CreateVM(i)

        # Disassociate the IP address from the VM
        core.disassociate_public_ip_address(mgmt.network_client(), i)
        log_message += "Public IP address unlinked"
        log_message += "--------------------------------------------\n"
        print("Public IP address unlinked\n----------------------------------------\n")



        # Get the private IP address of the newly created VM
        private_IP = core.getPrivateIpAddress(mgmt.network_client,i)
        # Write out the local IP to a reference file
        IP_File.write("VM_" + str(i) + "_Local_IP = " + private_IP + "\n")
    IP_File.close()


else:
    print("Just Testing Stuff")