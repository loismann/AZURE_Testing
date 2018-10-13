import threading, paramiko

class ssh:
    shell = None
    client = None
    transport = None

    def __init__(self,address,username,password):
        print("Connecting to server on ip", str(address) + ".")
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)
        self.transport = paramiko.Transport((address,22))
        self.transport.connect(username=username,password=password)
        thread = threading.Thread(target=self.process)
        thread.daemon = True
        thread.start()

    def sendCommand(self, command):
        if (self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print data when available
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.channel.recv(1024)
                        alldata += prevdata

                    print(str(alldata, "utf8"))
        else:
            print("Connection not opened.")

    def closeConnection(self):
        if(self.client != None):
            self.client.close()
            self.transport.close()

    def openShell(self,):
        self.shell = self.client.invoke_shell()

    def sendShell(self, command):
        if(self.shell):
            self.shell.send(command + "\n")
        else:
            print("Shell not opened")

    def process(self):
        global connection
        while True:
            #Print data when available
            if self.shell != None and self.shell.recv_ready():
                alldata = self.shell.recv(1024)
                while self.shell.recv_ready():
                    alldata += self.shell.recv(1024)
                    while self.shell != None and self.shell.recv_ready():
                        alldata += self.shell.recv(1024)
                    strdata = str(alldata, "utf8")
                    strdata.replace('\r', "")
                    print(strdata, end = "")
                    if(strdata.endswith("$ ")):
                        print("\n$ ", end = "")


# Run Code
# machine = "local"
# if machine == "local":
#     # PF Gmail Initial Cloud machine Credentials
#     sshUsername = "pferrer"
#     sshPassword = "Password_001"
#     sshServer = "127.0.0.1"
# elif machine == "GmailAzureCloud":
#     # PF Local Ubuntu Credentials
#     sshUsername = "pferrer"
#     sshPassword = "Password_001"
#     sshServer = "40.74.229.97"

sshUsername = "pferrer"
sshPassword = "Password_001"
sshServer = "127.0.0.1"

# Initialize connection (OPENSSH MUST ALREADY BE INSTALLED ON LINUX COMPUTER)
connection = ssh(sshServer,sshUsername,sshPassword)
connection.openShell()


# print("Connection Established")

#install radiance:
#Update Linux
connection.sendCommand("mkdir testfolder")
connection.sendCommand("mkdir testfolder2")
connection.sendCommand("wget https://www.radiance-online.org/software/snapshots/radiance-HEAD.tgz")
# connection.sendCommand("sudo apt-get update")
# connection.sendShell("Password_001")
# connection.sendShell("sudo apt-get install csh tcsh libtiff5 g++ g++4.1 tcl8.5 tk libc6-dev libx11-dev")
# connection.sendShell("sudo apt-get update")
# # connection.sendShell("wget https://www.radiance-online.org/software/snapshots/radiance-HEAD.tgz")
# connection.openShell()
# connection.sendShell("mkdir testfolder")



# or, if you like, send commands via the terminal.  Command must start with a " " (space)
# while True:
#     command = input("$ ")
#     if command.startswith(""):
#         command = command[1:]
#     connection.sendShell(command)
