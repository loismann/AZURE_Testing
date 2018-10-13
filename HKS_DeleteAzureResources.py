import time
from HELPERS.HELPER_Login_Info import *
from HELPERS.HELPER_SMS import SMS
import HELPERS.HELPER_Management_Clients
import _CORE_AUTOBUNTU as core


################################################# Run Code #############################################################
Delete_VMs = True

# Initialize Management Clients
if Delete_VMs:

    # Delete the resource group
    # Instantiate the management client class
    mgmt = HELPERS.HELPER_Management_Clients.MGMT()
    core.delete_resources(mgmt.resource_group_client())

    # Send the SMS Notification
    # Instantiate the SMS class
    sms = SMS()
    sms.DeleteResources()

else:
    print("Just Testing Stuff")