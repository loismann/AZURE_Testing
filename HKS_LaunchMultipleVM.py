import datetime
from HELPERS.HELPER_Login_Info import Login
from HELPERS.HELPER_SMS import SMS
import HELPERS.HELPER_Management_Clients
import _CORE_AUTOBUNTU as core
import os
import time
import multiprocessing



##########################################   Run Code   ################################################################

#Main Method for HKS_LaunchMultipleVM.py
def generate_vm(Generate_VM,i):
    # Initialize the Login Class from the Information File
    login = Login()

    # Initialize Management Clients
    mgmt = HELPERS.HELPER_Management_Clients.MGMT(login)
    # Instantiate the SMS class
    sms = SMS()

    # Run the VM Creation Loop
    if Generate_VM:
       # Start the sticky dictionary entry
        log_message = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create the resource group
        core.create_resource_group(mgmt.resource_group_client(login),login)
        log_message += "\nCreated Resource Group\n\n"




        log_message += "Creating Instance " + str(i) + " ...\n"
        print("Creating Instance " + str(i) + " ...")

        # Create a public IP address
        core.create_public_ip_address(mgmt.network_client(login), i,login)
        log_message += "IP Address Created\n"
        print("IP Address Created")

        # Create Network Interface
        core.create_HKSnic(mgmt.network_client(login), i,login)
        log_message += "Network Interface Created\n"
        print("Network Interface Created")

        # Create Custom VM
        core.create_customvm(mgmt.network_client(login), mgmt.compute_client(login), i, login)
        log_message += "VM Created\n"
        print("VM " + str(i) + " Created")
        # sms.CreateVM(i,login)
        # Connect to the machine and add the "man" Location from the usr folder

        # Disassociate the IP address from the VM
        core.disassociate_public_ip_address(mgmt.network_client(login), i, login)
        log_message += "Public IP address unlinked"
        log_message += "--------------------------------------------\n"
        print("Public IP address unlinked\n----------------------------------------\n")

    else:
        print("Just Testing Stuff: HKS_LaunchMultipleVM")


def main(VM_Count):
    # Multithreaded version
    print("main method of launch multiple vm file")
    Generate_VM = True
    jobs = []

    for i in range(VM_Count):
        p = multiprocessing.Process(target=generate_vm,
                                    args=(Generate_VM,i))
        jobs.append(p)
        p.start()

    for job in jobs:
        job.join()

    print("Finished creating VM's - moving on to Collecting IP Addresses")


    # After all the VM's have been made and are done, create (or override) an empty file to hold the Local IP addresses
    # initialize login class
    login = Login()
    # Initialize Management Clients
    mgmt = HELPERS.HELPER_Management_Clients.MGMT(login)
    print("Collecting Local IP Addresses")
    IP_File = open(os.path.join(os.getcwd(), 'HELPERS', 'Local_IP_Addresses.py'), 'a')
    for i in range(VM_Count):
        # Get the private IP address of the newly created VM
        private_IP = core.getPrivateIpAddress(mgmt.network_client(login),i, login)
        # Write out the local IP to a reference file
        IP_File.write("VM_" + str(i) + "_Local_IP = " + private_IP + "\n")
    IP_File.close()
    print("Finished Collecting Local IP Addresses")



