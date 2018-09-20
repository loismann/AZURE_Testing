import os
import getpass
import scriptcontext as sc
paramiko = sc.sticky['paramiko']
import time
scp = sc.sticky['scp']
pysftp = sc.sticky['pysftp']



# Pull the sticky value for the number of VMs
if sc.sticky.has_key("Global_VM_Count"):
    VM_Count = sc.sticky["Global_VM_Count"]
else:
    print "VM Count Not Detected"



#General Variables
SUBSCRIPTION_ID = '1153c71f-6990-467b-b1ec-c2ba46824d64'
GROUP_NAME = 'AUTOBUNTU_' + str(getpass.getuser())
LOCATION = 'southcentralus'
VM_NAME = 'AutoBuntu'
ADMIN_NAME = str(getpass.getuser())
ADMIN_PSWD = "Password_001"

############################################## SUPPORTING RESOURCE SETUP ###############################################

#This gets all Active Directory credentials
def get_credentials():
    credentials = sc.sticky['azure.common.credentials'].ServicePrincipalCredentials(
        client_id = '36783696-531f-4a87-8276-b6e477560a0c',
        secret = '2kvy1gZpynDzcluutR+Vw2WE2DcOshPH5u2gVvw/JX0=',
        tenant = '0ce7a0d4-9659-4ec3-bda3-9388f55c55af'
    )

    return credentials

#Instantiate all the management clients:
def instantiateMgmtClient():
    # Run the credentials function
    credentials = get_credentials()

    # Initialize Management Clients
    resource_group_client = sc.sticky['azure.mgmt.resource'].ResourceManagementClient(
        credentials,
        SUBSCRIPTION_ID
    )

    network_client = sc.sticky['azure.mgmt.network'].NetworkManagementClient(
        credentials,
        SUBSCRIPTION_ID
    )

    compute_client = sc.sticky['azure.mgmt.compute'].ComputeManagementClient(
        credentials,
        SUBSCRIPTION_ID
    )
    return [resource_group_client,network_client,compute_client]

def getVMinstance():
    # Find out how many active VM's are in existence
    # Create an object that is the VM instance
    vm = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME + "-" + str(i), expand='instanceView')

    # Unfortunate and convoluted way of obtaining public IP of selected instance
    ni_reference = vm.network_profile.network_interfaces[0]
    ni_reference = ni_reference.id.split('/')
    ni_group = ni_reference[4]
    ni_name = ni_reference[8]

    net_interface = network_client.network_interfaces.get(ni_group, ni_name)
    ip_reference = net_interface.ip_configurations[0].public_ip_address
    ip_reference = ip_reference.id.split('/')
    ip_group = ip_reference[4]
    ip_name = ip_reference[8]

    public_ip = network_client.public_ip_addresses.get(ip_group, ip_name)
    public_ip = public_ip.ip_address
    return public_ip

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

    except Exception, e:
        print
        "Something went wrong: %s" % str(e)

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
    time.sleep(5)
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
    ssh_client.connect(IP_Address,username=username,password=password,port=port)
    # print scp.SCPClient
    tr = ssh_client.get_transport()
    print type(tr)
    # tr.default_max_packet_size = 10000000000
    # tr.default_window_size = 10000000000
    # scp_run = scp.SCPClient(tr)
    # scp_run.put(source,destination)
    # time.sleep(4)
    # scp_run.close()
    # tr.close()

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
    print "did something"

###########################################  RUN CODE ####################################################



if Run:
    # Main: Get the IP addresses of the machines currently in use
    # Sub: Instantiate the Azure clients
    resource_group_client = instantiateMgmtClient()[0]
    network_client = instantiateMgmtClient()[1]
    compute_client = instantiateMgmtClient()[2]

    # Sub: Find the resource group that the user created
    myresource_group = None
    for item in resource_group_client.resource_groups.list():
        if str(getpass.getuser()) in str(item):
            myresource_group = item.name

    # #Sub: List the resources that are in the group we just found
    # for item in resource_group_client.resources.list_by_resource_group(myresource_group):
    #     if "Microsoft.Compute/virtualMachines" in str(item):
    #         print item

    # List of IP addresses
    IP_Addresses = []
    for i in range(VM_Count):
        IP = getVMinstance()
        IP_Addresses.append(IP)
    print IP_Addresses

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

    for root, dirs, files in os.walk(os.path.abspath(study_folder)):
        for file in files:
            # print file
            original_file_path = os.path.join(root, file)
            if not original_file_path.endswith(".bat"):
                # print original_file_path
                destination_file_path = "/home/pferrer/" + file
                # print destination_file_path
                fixfile(original_file_path)

                # There are multiple functions defined above trying to do more or less the same thing
                copyfilepysftp(IP_Addresses[0],22,ADMIN_NAME,ADMIN_PSWD,original_file_path,destination_file_path)
                # ftp_client = ssh_client.open_sftp()
                # ftp_client.put(old_file_path, destination_file_path)
                # ftp_client.close()
                # time.sleep(5)
                #client.close()

