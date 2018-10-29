
from HELPERS.HELPER_Login_Info import Login
from HELPERS.HELPER_SMS import SMS
import HELPERS.HELPER_Management_Clients
import _CORE_AUTOBUNTU as core
import os



################################################# Run Code #############################################################
Delete_VMs = True

# Initialize Management Clients
if Delete_VMs:

    #Initialize Login Information
    Login = Login()

    # Delete the resource group
    # Instantiate the management client class
    mgmt = HELPERS.HELPER_Management_Clients.MGMT(Login)
    client = mgmt.resource_group_client(Login)
    for item in client.resource_groups.list():
        if item.name == Login.GROUP_NAME:
            core.delete_resources(mgmt.resource_group_client(Login),Login)

            # Send the SMS Notification
            # Instantiate the SMS class
            sms = SMS()
            sms.DeleteResources(Login)
            IP_List_File = os.path.join(os.getcwd(), 'HELPERS', 'Local_IP_Addresses.py')
            if os.path.isfile(IP_List_File):
                os.remove(IP_List_File)
                print("IP File Found and Deleted")
            else:
                print("IP File Not Detected")
            print("Resource Group Deleted")
        else:
            IP_List_File = os.path.join(os.getcwd(), 'HELPERS', 'Local_IP_Addresses.py')
            if os.path.isfile(IP_List_File):
                os.remove(IP_List_File)
                print("IP File Found and Deleted")
            else:
                print("IP File Not Detected")

else:
    print("Just Testing Stuff")