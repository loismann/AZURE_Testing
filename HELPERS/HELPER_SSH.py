import paramiko
import scp
import paramiko
import pysftp



# This Class governs connections to the VM so commands can be run
class pf_ssh:
    client = None

    def __init__(self,address,port,username,password):
        # Let the user know we're connecting to the server
        print("Connecting to server...")
        # Create a new SSH client
        self.client = paramiko.SSHClient()
        # The following line is required if you want to script to be able to access a server thats not yet in the known_hosts file

        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Make the connection
        self.client.connect(address,port,username,password)


    def sendCommand(self,command):
        # Check to see if connection has been made previously
        if(self.client):
            stdin,stdout,stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print stdout data when available
                if stdout.channel.recv_ready():
                    # Retrieve the first 1024 bytes
                    alldata = stdout.channel.recv(1024)
                    while stdout.channel.recv_ready():
                        # Retrieve the next 1024 bytes
                        alldata += stdout.channel.recv(1024)

                    # Print as string with utf8 encoding
                    print(str(alldata, "utf8"))
        else:
            print("Connection not opened.")

    # Copy the files over from the local computer to a remote computer
    def copyfilesSCP(self,IP_Address, port, username, password, source, destination):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(IP_Address, port=port, username=username, password=password)
        tr = ssh_client.get_transport()
        tr.default_max_packet_size = 1000000000
        tr.default_window_size = 1000000000
        scp_run = scp.SCPClient(tr)
        scp_run.put(source, destination)
        scp_run.close()
        tr.close()

    def checkForDirectory(self,IP_Address, username, password, directoryToCheck):
        connection = pysftp.Connection(host=IP_Address,username=username,password=password)
        try:
            connection.chdir(directoryToCheck)
            pathExists = True
        except:
            pathExists = False

        return(pathExists)
