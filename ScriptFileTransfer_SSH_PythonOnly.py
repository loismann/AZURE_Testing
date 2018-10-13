import os
import paramiko
import time
import scp
import pysftp
from HELPER_Login_Info import *

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient







############################################## SUPPORTING RESOURCE SETUP ###############################################

#This gets all Active Directory credentials
def get_credentials():
    credentials = ServicePrincipalCredentials(
        client_id = APPLICATION_ID,
        secret = AUTHENTICATION_KEY,
        tenant = DIRECTORY_ID
    )

    return credentials

#Instantiate all the management clients:
def instantiateMgmtClient():
    # Run the credentials function
    credentials = get_credentials()

    # Initialize Management Clients
    resource_group_client = ResourceManagementClient(
        credentials,
        SUBSCRIPTION_ID
    )

    network_client = NetworkManagementClient(
        credentials,
        SUBSCRIPTION_ID
    )

    compute_client = ComputeManagementClient(
        credentials,
        SUBSCRIPTION_ID
    )
    return [resource_group_client,network_client,compute_client]

def getVMinstance():
    # Find out how many active VM's are in existence
    # Create an object that is the VM instance
    vm = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME)
    private_ip = vm.ip_configurations[0].private_ip_address
    return private_ip


def getPrivateIP(network_client):
    nic = network_client.network_interfaces.get(Network_GROUP_NAME, 'AUTOBUNTU_myNic', )
    ip =  nic.ip_configurations[0].private_ip_address
    return ip


class ssh:
    client = None

    def __init__(self, address, username, password):
        # Let the user know we're connecting to the server
        print("Connecting to server...")
        # Create a new SSH client
        self.client = client.SSHClient()
        # The following line is required if you want to script to be able to access a server thats not yet in the known_hosts file
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        # Make the connection
        self.client.connect(address,username=username,password=password,look_for_keys=False)

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

def bat_to_sh(file_path):
    """Convert a honeybee .bat file to .sh file.

    WARNING: This is a very simple function and doesn't handle any edge cases.
    """
    sh_file = file_path[:-4] + '.sh'
    with open(file_path, 'rb') as inf, open(sh_file, 'wb') as outf:
        # print inf
        outf.write('#!/usr/bin/env bash\n\n')
        row = inf.readlines()
        # print row
        for line in row:
            # pass the path lines, etc to get to the commands
            if line.strip():
                continue
            else:
                break

        for line in row:
            # print line
            if line.startswith('echo'):
                continue
            # replace c:\radiance\bin and also chanege \\ to /
            modified_line = line.replace('c:\\radiance\\bin\\', '').replace('\\', '/')
            outf.write(modified_line)

    # print('bash file is created at:\n\t%s' % sh_file)
    return sh_file

def executeBatchFiles(self, batchFileNames, maxPRuns=None, shell=False, waitingTime=0.5):
    """Run a number of batch files in parallel and
        wait to end of the analysis.

        Args:
            batchFileNames: List of batch files
            maxPRuns: max number of files to be ran in parallel (default = 0)
            shell: set to True if you do NOT want to see the cmd window while the analysis is runnig
    """

    if not maxPRuns: maxPRuns = 1
    maxPRuns = int(maxPRuns)
    total = len(batchFileNames)

    if maxPRuns < 1: maxPRuns = 1
    if maxPRuns > total: maxPRuns = total

    running = 0
    done = False
    jobs = []
    pid = 0

    try:
        while not done:
            if running < maxPRuns and pid < total:
                # execute the files
                jobs.append(subprocess.Popen(batchFileNames[pid].replace("\\", "/"), shell=shell))
                pid += 1
                time.sleep(waitingTime)

            # count how many jobs are running and how many are done
            running = 0
            finished = 0
            for job in jobs:
                if job.poll() is None:
                    # one job is still running
                    running += 1
                else:
                    finished += 1

            if running == maxPRuns:
                # wait for half a second
                # print "waiting..."
                time.sleep(waitingTime)

            if finished == total:
                done = True

    except Exception as e:
        print("Something went wrong: %s" % str(e))

def runBatchFiles(self, initBatchFileName, batchFileNames, fileNames, \
                  pcompBatchFile, waitingTime, runInBackground=False):
    self.executeBatchFiles([initBatchFileName], maxPRuns=1, shell=runInBackground, waitingTime=waitingTime)
    self.executeBatchFiles(batchFileNames, maxPRuns=len(batchFileNames), shell=runInBackground, waitingTime=waitingTime)

    if pcompBatchFile != "":
        os.system(pcompBatchFile)  # put all the files together

def collectResults(self, subWorkingDir, radFileName, numOfCPUs, analysisRecipe, expectedResultFiles):
    if analysisRecipe.type == 2:
        # annual simulation
        runAnnualGlare = analysisRecipe.DSParameters.runAnnualGlare
        onlyAnnualGlare = analysisRecipe.DSParameters.onlyAnnualGlare
        numOfIllFiles = analysisRecipe.DSParameters.numOfIll
        annualGlareViews = analysisRecipe.DSParameters.RhinoViewsName
        DSResultFilesAddress = []

        if not (runAnnualGlare and onlyAnnualGlare):
            # read the number of .ill files
            # and the number of .dc files
            if subWorkingDir[-1] == os.sep: subWorkingDir = subWorkingDir[:-1]
            startTime = time.time()

            # check if the results are available
            files = os.listdir(subWorkingDir)
            numIll = 0
            numDc = 0
            for file in files:
                if file.EndsWith('ill'):
                    DSResultFilesAddress.append(os.path.join(subWorkingDir, file))
                    numIll += 1
                elif file.EndsWith('dc'):
                    numDc += 1
            # /2 in case of conceptual dynamic blinds in Daysim
            if numIll != numOfCPUs * numOfIllFiles or not \
                    (numDc == numOfCPUs * numOfIllFiles or \
                     numDc == numOfCPUs * numOfIllFiles / 2):
                print
                "Can't find the results for the study"
                DSResultFilesAddress = []

        # check for results of annual glare analysis if any
        annualGlareResults = {}
        for view in annualGlareViews:
            if view not in annualGlareResults.keys():
                annualGlareResults[view] = []

        dgpFile = os.path.join(subWorkingDir, radFileName + '_0.dgp')

        if runAnnualGlare and os.path.isfile(dgpFile):
            with open(dgpFile, "r") as dgpRes:
                for line in dgpRes:
                    try:
                        hourlyRes = line.split(" ")[4:]
                        # for each view there should be a number
                        for view, res in zip(annualGlareViews, hourlyRes):
                            annualGlareResults[view].append(res.strip())
                    except:
                        pass

        return DSResultFilesAddress, annualGlareResults

    elif analysisRecipe.type == 0:
        # image-based analysis
        return expectedResultFiles

    else:
        RADResultFilesAddress = expectedResultFiles
        # grid-based analysis
        numRes = 0
        files = os.listdir(subWorkingDir)
        for file in files:
            if file.EndsWith('res'): numRes += 1
        if numRes != numOfCPUs:
            print
            "Cannot find the results of the study"
            RADResultFilesAddress = []
        time.sleep(1)
        return RADResultFilesAddress

def copyfile(IP_Address, port, username, password, source, destination):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    t = paramiko.Transport(IP_Address, port)
    t.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.put(source,destination)
    sftp.close()
    t.close()

def copyfile2(IP_Address,username,password,port,source,destination):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()

    client.connect(IP_Address,username=username,password=password,port=port)
    tr = client.get_transport()
    tr.default_max_packet_size = 10000000000
    tr.default_window_size = 10000000000
    sftp = client.open_sftp()
    sftp.put(source,destination)

def copyfilescp(IP_Address,username,password,port,source,destination):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(IP_Address, port, username, password)

    return client

def copyfilesscp2(IP_Address, port, username, password, source, destination):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(IP_Address, port=port, username=username, password=password)
    tr = ssh_client.get_transport()
    tr.default_max_packet_size = 1000000000
    tr.default_window_size = 1000000000
    scp_run = scp.SCPClient(tr)
    scp_run.put(source,destination)
    scp_run.close()
    tr.close()

def copyfilepysftp(IP_Address, port, username, password, source, destination):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(host=IP_Address, port=port, username=username, password=password, cnopts=cnopts) as sftp:
        sftp.put(source,preserve_mtime=True)
        sftp.close()

def fixfile(filename):
    windows_line_ending = '\r\n'
    linux_line_ending = '\n'
    with open(filename, 'rb') as f:
        content = f.read()
        content = content.replace(windows_line_ending, linux_line_ending)
    with open(filename, 'wb') as f:
        f.write(content)
    print("did something")

###########################################  RUN CODE ####################################################

Run = True

if Run:
    # Main: Get the IP addresses of the machines currently in use
    # Sub: Instantiate the Azure clients
    resource_group_client = instantiateMgmtClient()[0]
    network_client = instantiateMgmtClient()[1]
    compute_client = instantiateMgmtClient()[2]

    ip = getPrivateIP(network_client)
    print(ip)
    # Sub: Find the resource group that the user created
    # myresource_group = None
    # for item in resource_group_client.resource_groups.list():
    #     if str(getpass.getuser()) in str(item):
    #         myresource_group = item.name

    # #Sub: List the resources that are in the group we just found
    # for item in resource_group_client.resources.list_by_resource_group(myresource_group):
    #     if "Microsoft.Compute/virtualMachines" in str(item):
    #         print item

    # List of IP addresses
    # IP_Addresses = []
    # for i in range(VM_Count):
    #     IP = getVMinstance()
    #     IP_Addresses.append(IP)
    # print IP_Addresses

    # Find the directory where all the batch files are written
    # Go through all the folders and files in the simulation folder
    # for root, dirs, files in os.walk(os.path.abspath(study_folder)):
    #     for file in files:
    #         file_path = os.path.join(root, file)
    #         if file_path.endswith(".bat"):
    #             # print file_path
    #             bat_to_sh(file_path)

    # For the Glare analysis, figure out how many simulation folders need to go to each machine
    # This will be the total number of hours being run divided by the total number of VM instances

    # Connect to virtual machine and run a command


    # This line allows the SSH client to connect without asking if you want to trust

    #ssh_client.connect(hostname=IP_Addresses[0],username=ADMIN_NAME,password=ADMIN_PSWD)

    #test command
    # stdin, stdout, stderr = ssh_client.exec_command("sudo mkdir testfolder testfolder2")
    # stdin,stdout,stderr = ssh_client.exec_command("sudo ls")
    # print stdout.readlines()

    #test sending file (It works!!!!)
    # ftp_client = ssh_client.open_sftp()
    # ftp_client.put(r"C:\Users\pferrer\Desktop\test.txt","/datadrive/test.txt")
    # ftp_client.close()

    # test sending all relevant files in a folder
    study_folder = "C:\\ladybug\\AzurePFGlareTesting\\21MAR600\\imageBasedSimulation"
    for root, dirs, files in os.walk(os.path.abspath(study_folder)):
        for file in files:
            original_file_path = os.path.join(root, file)
            if not original_file_path.endswith(".bat"):
                # print original_file_path
                destination_file_path = "/home/pferrer/" + file
                # print destination_file_path
                # fixfile(original_file_path)
            #
            #     # There are multiple functions defined above trying to do more or less the same thing
                copyfile(ip,22,ADMIN_NAME,ADMIN_PSWD,original_file_path,destination_file_path)
            #     # ftp_client = ssh_client.open_sftp()
            #     # ftp_client.put(old_file_path, destination_file_path)
            #     # ftp_client.close()
            #     # time.sleep(5)
            #     #client.close()

