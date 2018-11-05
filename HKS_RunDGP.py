import subprocess
import os
import time
import math
from collections import defaultdict
from HELPERS.HELPER_SSH import ssh
import shutil


# TODO: 1. Convert batch files to shell files
class Convert:
    def __init__(self):
        self.nothing = None

    # This converts the bat files to shell files
    def bat_to_sh_DGP(self, file_path):
        sh_file = file_path[:-4] + '.sh'
        with open(file_path, 'r') as infile, open(sh_file, 'w') as outfile:
            outfile.write('#!/usr/bin/env bash\n\n')
            for i,line in enumerate(infile):
                if i <4:
                    pass
                else:
                    # Go through each string looking for file paths
                    # if you find file paths, replace them with just the file name
                    parse = line.strip().split()
                    replaced = []
                    if parse:
                        for segment in parse:
                            if os.path.exists(segment):
                                replaced.append(os.path.basename(segment))
                                print("found a file!")
                            else:
                                replaced.append(segment)
                        new_line = " ".join(replaced)
                        outfile.write(new_line + '\n')
            outfile.close()

    # This removes carriage returns (thanks sarith)
    def sarithFixFile(self):
        for fname in os.listdir(os.getcwd()):
            if ".sh" in fname and "new" not in fname:
                name, ext = os.path.splitext(fname)
                newname = name + "new." + ext
                with open(fname) as f, open(newname, "w") as f2:
                    for lines in f:
                        if lines.strip():
                            f2.write(lines.strip() + '\n')
                        print(list(lines))
                os.rename(newname, fname)

    # This doesnt really do anything!
    def fixfile(self,filename):
        windows_line_ending = '\r\n'
        linux_line_ending = '\n'
        with open(filename, 'r') as f:
            content = f.read()
            content = content.replace(windows_line_ending, linux_line_ending)
        with open(filename, 'w') as f:
            f.write(content)


# TODO: 2. Create Master functions to control the Linux Operations

# This kicks off the batch files
def excecuteBatchFiles(batchFileNames, maxPRuns=None, shell=True, waitingTime=0.5):
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

                # jobs.append(subprocess.Popen(["bash", batchFileNames[pid]]))
                jobs.append(os.system("bash %s"% batchFileNames[pid]))

                pid += 1
                print("Batch File: " + batchFileNames[pid] + " Launched")
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

# This actually runs the batch files
def RUN_BatchFiles(initBatchFileName, batchFileNames, pcompBatchFile, waitingTime=0.5, runInBackground=False):
    excecuteBatchFiles([initBatchFileName], maxPRuns=1, shell=runInBackground, waitingTime=waitingTime)
    excecuteBatchFiles(batchFileNames, maxPRuns=len(batchFileNames), shell=runInBackground, waitingTime=waitingTime)

    if pcompBatchFile != "":
        os.system(pcompBatchFile)  # put all the files together

# This goes through each subfolder and collects the files so they can be used as inputs in the "RUN_BatchFiles" function
def FIND_BatchFileTypes(directory):
    # Prepare the inputs for the "run batch file" functions
    batchFile_parameters = {}
    batchFile_parameters['supportingBatchFiles'] = []

    for root, dirs, files in os.walk(os.path.abspath(directory)):
        for file in files:
            file_path = os.path.join(root, file)

            # If it runs across a pcomp file, add it to the dictionary
            if file_path.endswith(".sh") and "PCOMP" in file_path:
                # print("found the precomp file")
                batchFile_parameters["pcompBatchFile"] = file_path

            # If it runs across an init file, add it to the dictionary
            elif file_path.endswith(".sh") and "Init" in file_path:
                # print("found the init file")
                batchFile_parameters["initBatchFileName"] = file_path

            # When it runs across any other sh files in the directory add them too
            elif file_path.endswith(".sh"):
                # print("found a supporting file")
                batchFile_parameters["supportingBatchFiles"].append(file_path)

    return batchFile_parameters

# This will get the number of VM's in use from the local copy of the IP Address file
def GET_VMCount():
    vm_count = 0
    try:
        scriptdirectory = os.path.dirname(__file__)  # <-- Absolute path of this file
        path = os.path.join(scriptdirectory, "HELPERS/Local_IP_Addresses.py")
        with open(path) as IP:
            for line in IP:
                if "IP" in line:
                    vm_count += 1

    except:
        print("No copy of 'Local_IP_Addresses.py' found. Are VM's active?")
    return vm_count

# This will get the VM IP addresses as a list
def GET_VMIP():
    IP_Addresses = []
    try:
        scriptdirectory = os.path.dirname(__file__)  # <-- Absolute path of this file
        path = os.path.join(scriptdirectory, "HELPERS/Local_IP_Addresses.py")
        with open(path) as IP:
            for line in IP:
                if "IP" in line:
                    words = line.split()
                    for word in words:
                        if "IP" not in word and "=" not in word:
                            IP_Addresses.append(word)
    except:
        print("No copy of 'Local_IP_Addresses.py' found. Are VM's active?")
    return IP_Addresses



# TODO: 3. Copy all files over to linux
# if Run:
#     # Main: Get the IP addresses of the machines currently in use
#     # Sub: Instantiate the Azure clients
#
#     #Main Folder Location:
#     study_folder = input("Paste Folder Location of .bat files for conversion:")
#
#     resource_group_client = instantiateMgmtClient()[0]
#     network_client = instantiateMgmtClient()[1]
#     compute_client = instantiateMgmtClient()[2]
#
#     # Sub: Find the resource group that the user created
#     myresource_group = None
#     for item in resource_group_client.resource_groups.list():
#         if "AUTOBUNTU" in str(item):
#             myresource_group = item.name
#
#     # Main: List of IP addresses
#     privateIpAddresses = []
#     for i in range(VM_Count):
#         privateIP = getPrivateIpAddress(network_client, i)
#         privateIpAddresses.append(privateIP)
#     print(privateIpAddresses)
#
#     # Main: Find the directory where all the batch files are written
#     # Sub: Go through all the folders and files in the simulation folder
#     for root, dirs, files in os.walk(os.path.abspath(study_folder)):
#         for file in files:
#             file_path = os.path.join(root, file)
#             if file_path.endswith(".bat"):
#                 # print file_path
#                 bat_to_sh(file_path)
#
#     # For the Glare analysis, figure out how many simulation folders need to go to each machine
#     # This will be the total number of hours being run divided by the total number of VM instances
#
#     # Connect to virtual machine and Copy over Base Project files
#     for i in range(VM_Count):
#         for root, dirs, files in os.walk(os.path.abspath(study_folder)):
#             for file in files:
#                 # print file
#                 original_file_path = os.path.join(root, file)
#                 if not original_file_path.endswith(".bat"):
#                     # print original_file_path
#                     destination_file_path = "/home/pferrer/" + file
#                     # print destination_file_path
#                     fixfile(original_file_path)
#                     copyfilesSCP(privateIpAddresses[i],
#                                   22,
#                                   sc.sticky['Login_Info'].ADMIN_NAME,
#                                   sc.sticky['Login_Info'].ADMIN_PSWD,
#                                   original_file_path,
#                                   destination_file_path,
#                                   )
#     print("Files Copied")
#
#
#
# # TODO: 4. Run the Master Python file to create and manage jobs
# ##### Run Code
# if __name__ == "__main__":
#     # Get the main directory we're working in
#     Main_Directory = "/home/pferrer"
#     # Find the different inputs for running the batch files
#     params = FIND_BatchFileTypes(Main_Directory)
#     print(params)
#
#     # print(params.get('pcompBatchFile'))
#     # Deep Breath.... Run all the batch files
#     RUN_BatchFiles(params.get('initBatchFileName'),params.get('supportingBatchFiles'), params.get('pcompBatchFile'))



########################################################################################################################
""" Step 1: Walk through all the folders in the study folder and convert the  batch files to bash files 
    Step 2: While walking through the directory tree, also remove all the rad files except two.  Only one copy of rad 
            and material rad will be used per virtual machine.  Rename the rad files and place them outside the hourly
            directory tree
"""

##### Various Locations for Main Direcotry dependent upon testing environment
# Main_Directory = input("Paste Folder Location of .bat files for conversion:")
# Main_Directory = "C:\ladybug\AzurePFGlareTesting"
Main_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles"

# Walk the Directory and Convert the batch files
# At the same time, isolate a copy of the rad files outside the folder structure, and then
# delete all the other rad files encountered in the folders

# These variables will hold a copy of the rad files
mat_rad = None
object_rad = None

for root, dirs, files in os.walk(os.path.abspath(Main_Directory)):
    for file in files:
        file_path = os.path.join(root, file)
        if file_path.endswith(".bat"):
            Convert().bat_to_sh_DGP(file_path)
            Convert().sarithFixFile()
            os.remove(file_path)
        # This will set the rad variables to the first copy of the rad files encountered
        elif mat_rad == None or object_rad == None and file_path.endswith(".rad"):
            if "material" in file_path:
                mat_rad = file_path
            else:
                object_rad = file_path
        # If the variables have already been set, remove all the rad files that are encountered
        elif file_path.endswith(".rad"):
            os.remove(file_path)

shutil.move(mat_rad,Main_Directory)
shutil.move(object_rad,Main_Directory)
# print(mat_rad)
# print(object_rad)





""" Step 3: figure out how to copy over the files to the vm:
            Identify how many VMs there are
            Copy over ONE COPY of the rad files to each VM
            Divide the number of hourly directories by the number of vm's
            and send each group of directories to the correct VM
"""
# Get the count and IP addresses of the currently assigned VM's
vm_count = GET_VMCount()
vm_IP_List = GET_VMIP()

# folders = (os.listdir(Main_Directory))
# chunk_size = math.ceil(len(folders)/vm_count)

# # Look more into how this works, but this will split the folder names into even chunks based on the number of VMs
# # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
# blah = [folders[i:i + chunk_size] for i in range(0, len(folders), chunk_size)]
# print(blah)




# folder_split = {}
# for i in range(vm_count):
#     folder_split["FolderGroup_" + str(i)] = []
#
# for i in range(len(os.listdir(Main_Directory))):
#     print(i)
#
# print(folder_split)
#
