
from HELPERS.HELPER_Login_Info import Login
from HELPERS.HELPER_SMS import SMS
import HELPERS.HELPER_Management_Clients
import _CORE_AUTOBUNTU as core
import os



login = Login()
################################################# Run Code #############################################################

# Main method for HKS_DeleteAzureResources.py
def main(Local_Repo_Directory,Delete_VMs=True):
    # Initialize Management Clients
    if Delete_VMs:
        print("running")

        #Initialize Login Information


        # Delete the resource group
        # Instantiate the management client class
        mgmt = HELPERS.HELPER_Management_Clients.MGMT(login)
        client = mgmt.resource_group_client(login)
        found_machine = None
        for item in client.resource_groups.list():
            if item.name == login.GROUP_NAME:
                core.delete_resources(mgmt.resource_group_client(login),login)
                found_machine = "Found and Deleted Resources"

                # Send the SMS Notification
                # Instantiate the SMS class
                sms = SMS()
                sms.DeleteResources(login)
                IP_List_File = os.path.join(os.getcwd(), 'HELPERS', 'Local_IP_Addresses.py')
                if os.path.isfile(IP_List_File):
                    os.remove(IP_List_File)
                    # print("IP File Found and Deleted")
                else:
                    pass
                    # print("IP File Not Detected")
                print("Resource Group Deleted")
            else:
                IP_List_File = os.path.join(os.getcwd(), 'HELPERS', 'Local_IP_Addresses.py')
                if os.path.isfile(IP_List_File):
                    os.remove(IP_List_File)
                    # print("IP File Found and Deleted")
                else:
                    pass
                    # print("IP File Not Detected")
                # print("No Matching Resource Group Found - Moving On!")
        else:
            found_machine = "No Matching Resources Found >>> Moving On"
        print(found_machine + "\n")
    else:
        print("Just Testing Stuff: HKS_DeleteAzureResources")

    #Just in case... make absolutely sure to delete the IP file
    for path, directory, files in os.walk(Local_Repo_Directory):
        for file in files:
            file_path = os.path.join(path,file)
            if "Local" in file_path:
                print("IP Address File Found and Deleted")
                os.remove(file_path)




# If you need to run this file as __Main__:
# Local_Repo_Directory = login.Local_Repo_Directory
# main(Local_Repo_Directory,True)