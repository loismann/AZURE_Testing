from HELPER_Login_Info import *
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient



class MGMT:
    def __init__(self):
        self.credentials = self.get_credentials()


    def get_credentials(self):
        login = ServicePrincipalCredentials(
            client_id=APPLICATION_ID,
            secret=AUTHENTICATION_KEY,
            tenant=DIRECTORY_ID,
        )
        return login

    def resource_group_client(self):
        client = ResourceManagementClient(
            self.credentials,
            SUBSCRIPTION_ID
        )
        return client

    def network_client(self):
        client = NetworkManagementClient(
            self.credentials,
            SUBSCRIPTION_ID
        )
        return client

    def compute_client(self):
        client = ComputeManagementClient(
            self.credentials,
            SUBSCRIPTION_ID
        )
        return client