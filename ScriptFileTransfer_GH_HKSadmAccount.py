import os
import scriptcontext as sc
paramiko = sc.sticky['paramiko']
import time
scp = sc.sticky['scp']
pysftp = sc.sticky['pysftp']


# Pull the sticky value for the number of VMs
if sc.sticky.has_key("Global_VM_Count"):
    VM_Count = sc.sticky["Global_VM_Count"]
else:
    print("VM Count Not Detected")


############################################## SUPPORTING RESOURCE SETUP ###############################################

#This gets all Active Directory credentials
def get_credentials():
    credentials = sc.sticky['azure.common.credentials'].ServicePrincipalCredentials(
        client_id=sc.sticky['Login_Info'].APPLICATION_ID,
        secret=sc.sticky['Login_Info'].AUTHENTICATION_KEY,
        tenant=sc.sticky['Login_Info'].DIRECTORY_ID,
    )

    return credentials

#Instantiate all the management clients:
def instantiateMgmtClient():
    # Run the credentials function
    credentials = get_credentials()

    # Initialize Management Clients
    resource_group_client = sc.sticky['azure.mgmt.resource'].ResourceManagementClient(
        credentials,
        sc.sticky['Login_Info'].SUBSCRIPTION_ID
    )

    network_client = sc.sticky['azure.mgmt.network'].NetworkManagementClient(
        credentials,
        sc.sticky['Login_Info'].SUBSCRIPTION_ID
    )

    compute_client = sc.sticky['azure.mgmt.compute'].ComputeManagementClient(
        credentials,
        sc.sticky['Login_Info'].SUBSCRIPTION_ID
    )
    return [resource_group_client,network_client,compute_client]

# This will disassociate the public IP address from the VM after its created
def getPrivateIpAddress(network_client, Instance):
    nic = network_client.network_interfaces.get(sc.sticky['Login_Info'].GROUP_NAME,
                                                sc.sticky['Login_Info'].GROUP_NAME + '_myNic_' + str(Instance), )
    #https://docs.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.v2018_08_01.models.networkinterfaceipconfiguration?view=azure-python
    #https://github.com/Azure/azure-sdk-for-python/issues/695#issuecomment-236024219
    # This will dissassocate the public ip address from the VM:
    privateIP = nic.ip_configurations[0].private_ip_address
    # This updates the network interface that currently exists with the properties of the variable "nic" assigned above
    network_client.network_interfaces.create_or_update(sc.sticky['Login_Info'].GROUP_NAME,
                                                       sc.sticky['Login_Info'].GROUP_NAME + '_myNic_' + str(Instance),
                                                       nic)
    return privateIP

# This translates the bat files in the study folder into bash files
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

# Not sure the difference between this and "runBatchFiles"
def executeBatchFiles(self, batchFileNames, maxPRuns=None, shell=True, waitingTime=0.5):
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
        print "Something went wrong: %s" % str(e)

# Not sure the difference between this and "excecuteBatchFiles"
def runBatchFiles(self, initBatchFileName, batchFileNames, fileNames, \
                  pcompBatchFile, waitingTime, runInBackground=False):
    self.executeBatchFiles([initBatchFileName], maxPRuns=1, shell=runInBackground, waitingTime=waitingTime)
    self.executeBatchFiles(batchFileNames, maxPRuns=len(batchFileNames), shell=runInBackground, waitingTime=waitingTime)

    if pcompBatchFile != "":
        os.system(pcompBatchFile)  # put all the files together

# Does this need to be here?  It's referencing recipes from grasshopper.  Should this be in a separate "results" button?
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

# Copy the files over from the local computer to a remote computer
def copyfilesSCP(IP_Address, port, username, password, source, destination):
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

# This was originally in here to try and fix the file copy problem - not sure if this is still needed
def fixfile(filename):
    windows_line_ending = '\r\n'
    linux_line_ending = '\n'
    with open(filename, 'rb') as f:
        content = f.read()
        content = content.replace(windows_line_ending, linux_line_ending)
    with open(filename, 'wb') as f:
        f.write(content)


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
        if "AUTOBUNTU" in str(item):
            myresource_group = item.name

    # Main: List of IP addresses
    privateIpAddresses = []
    for i in range(VM_Count):
        privateIP = getPrivateIpAddress(network_client, i)
        privateIpAddresses.append(privateIP)
    print(privateIpAddresses)

    # Main: Find the directory where all the batch files are written
    # Sub: Go through all the folders and files in the simulation folder
    for root, dirs, files in os.walk(os.path.abspath(study_folder)):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(".bat"):
                # print file_path
                bat_to_sh(file_path)

    # For the Glare analysis, figure out how many simulation folders need to go to each machine
    # This will be the total number of hours being run divided by the total number of VM instances

    # Connect to virtual machine and Copy over Base Project files
    for i in range(VM_Count):
        for root, dirs, files in os.walk(os.path.abspath(study_folder)):
            for file in files:
                # print file
                original_file_path = os.path.join(root, file)
                if not original_file_path.endswith(".bat"):
                    # print original_file_path
                    destination_file_path = "/home/pferrer/" + file
                    # print destination_file_path
                    fixfile(original_file_path)
                    copyfilesSCP(privateIpAddresses[i],
                                  22,
                                  sc.sticky['Login_Info'].ADMIN_NAME,
                                  sc.sticky['Login_Info'].ADMIN_PSWD,
                                  original_file_path,
                                  destination_file_path,
                                  )
    print("Files Copied")