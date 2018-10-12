import time
from Login_Info import *

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption

# This gets all Active Directory credentials
def get_credentials():
    credentials = ServicePrincipalCredentials(
        client_id=APPLICATION_ID,
        secret=AUTHENTICATION_KEY,
        tenant=DIRECTORY_ID,
    )

    return credentials

#Delete All the Resources
def delete_resources(resource_group_client):
    creation_result = resource_group_client.resource_groups.delete(GROUP_NAME)
    while not creation_result.done():
        print("Deleting Resources...")
        time.sleep(10)

# Run Code
Delete_VMs = True
# Initialize Management Clients
if Delete_VMs:
    credentials = get_credentials()
    resource_group_client = ResourceManagementClient(
        credentials,
        SUBSCRIPTION_ID
    )
    delete_resources(resource_group_client)


else:
    print("Just Testing Stuff")