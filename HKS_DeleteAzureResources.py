import time
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
    core.delete_resources(mgmt.resource_group_client(Login),Login)

    # Send the SMS Notification
    # Instantiate the SMS class
    sms = SMS()
    sms.DeleteResources(Login)


else:
    print("Just Testing Stuff")