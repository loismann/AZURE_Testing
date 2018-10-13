
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient



class MGMT:
    def __init__(self,Login):
        self.credentials = self.get_credentials(Login)


    def get_credentials(self,Login):
        login_completed = ServicePrincipalCredentials(
            client_id=Login.APPLICATION_ID,
            secret=Login.AUTHENTICATION_KEY,
            tenant=Login.DIRECTORY_ID,
        )
        return login_completed

    def resource_group_client(self,Login_Class):
        client = ResourceManagementClient(
            self.credentials,
            Login_Class.SUBSCRIPTION_ID
        )
        return client

    def network_client(self,Login_Class):
        client = NetworkManagementClient(
            self.credentials,
            Login_Class.SUBSCRIPTION_ID
        )
        return client

    def compute_client(self,Login_Class):
        client = ComputeManagementClient(
            self.credentials,
            Login_Class.SUBSCRIPTION_ID
        )
        return client