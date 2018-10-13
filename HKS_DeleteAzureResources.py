import time
from HELPER_Login_Info import *
from HELPER_SMS import SMS
import HELPER_Management_Clients


#Delete All the Resources
def delete_resources(resource_group_client):
    creation_result = resource_group_client.resource_groups.delete(GROUP_NAME)
    while not creation_result.done():
        print("Deleting Resources...")
        time.sleep(10)



################################################# Run Code #############################################################
Delete_VMs = True

# Initialize Management Clients
if Delete_VMs:

    # Delete the resource group
    # Instantiate the management client class
    mgmt = HELPER_Management_Clients.MGMT()
    delete_resources(mgmt.resource_group_client())

    # Send the SMS Notification
    # Instantiate the SMS class
    sms = SMS()
    sms.DeleteResources()

else:
    print("Just Testing Stuff")