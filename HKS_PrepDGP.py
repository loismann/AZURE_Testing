import subprocess
import os
import time
import math
from collections import defaultdict
from HELPERS.HELPER_SSH import pf_ssh
import shutil
from HELPERS.HELPER_Login_Info import Login
import HELPERS.HELPER_SMS as sms



# TODO: 1. Convert batch files to shell files
class Convert:
    def __init__(self):
        self.nothing = None

    # This converts the bat files to shell files
    def bat_to_sh_DGP(self, file_path):
        sh_file = file_path[:-4] + '.sh'
        with open(file_path, 'r') as infile, open(sh_file, 'w') as outfile:
            outfile.write('#!/usr/bin/env bash\n')
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
                            if "del" in segment:
                                replaced.append("rm")
                            if os.path.exists(segment):
                                found_a_file = segment
                                if ".rad" and "material" in found_a_file:
                                    redirection = "../Materials.rad"
                                    replaced.append(redirection)
                                elif ".rad" in found_a_file and "material" not in found_a_file:
                                    redirection = "../Objects.rad"
                                    replaced.append(redirection)
                                else:
                                    replaced.append(os.path.basename(segment))
                                # print("found a file!")

                            else:
                                replaced.append(segment)

                        new_line = " ".join(replaced)
                        outfile.write(new_line + '\n')
            outfile.close()

    # This removes carriage returns (thanks sarith)
    def sarithFixFile(self, directory):
        for root, dir, fname in os.walk(directory):
            if ".sh" in fname and "new" not in fname:
                name, ext = os.path.splitext(fname)
                newname = name + "new." + ext
                with open(fname) as f, open(newname, "w") as f2:
                    for lines in f:
                        if lines.strip():
                            f2.write(lines.strip() + '\n')
                        print(list(lines))
                os.rename(newname, fname)

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

# This will convert batch files and strip/reposition rad files
def prepareFileTransfer(Local_Main_Directory):
    # These variables will hold a copy of the rad files
    mat_rad = None
    object_rad = None
    Rad_Files_For_Transfer = []

    convert = Convert()
    for root, dirs, files in os.walk(os.path.abspath(Local_Main_Directory)):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(".bat"):
                convert.bat_to_sh_DGP(file_path)
                convert.sarithFixFile(Local_Main_Directory)
                os.remove(file_path)
            # This will set the rad variables to the first copy of the rad files encountered
            elif (mat_rad == None or object_rad == None) and file_path.endswith(".rad"):
                if "material" in file_path:
                    mat_rad = file_path
                else:
                    object_rad = file_path
            # If the variables have already been set, remove all the rad files that are encountered
            elif file_path.endswith(".rad"):
                os.remove(file_path)

    moved1 = os.path.join(Local_Main_Directory, "Materials.rad")
    moved2 = os.path.join(Local_Main_Directory, "Objects.rad")
    os.rename(shutil.move(mat_rad, Local_Main_Directory), moved1 )
    os.rename(shutil.move(object_rad, Local_Main_Directory), moved2)
    Rad_Files_For_Transfer.append(moved1)
    Rad_Files_For_Transfer.append(moved2)

    return Rad_Files_For_Transfer



########################################################################################################################
""" Step 1: Walk through all the folders in the study folder and convert the  batch files to bash files 
    Step 2: While walking through the directory tree, also remove all the rad files except two.  Only one copy of rad 
            and material rad will be used per virtual machine.  Rename the rad files and place them outside the hourly
            directory tree
"""

##### Various Locations for Main Direcotry dependent upon testing environment
# Local_Main_Directory = input("Paste Folder Location of .bat files for conversion:")
# Local_Main_Directory = r"C:\Users\pferrer\Desktop\test"
Local_Main_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles"
Azure_Main_Directory = "/home/pferrer/new"

# Walk the Directory and Convert the batch files
# At the same time, isolate a copy of the rad files outside the folder structure, and then
# delete all the other rad files encountered in the folders
Rad_Files_For_Transfer = prepareFileTransfer(Local_Main_Directory)

""" Step 3: figure out how to copy over the files to the vm:
            Identify how many VMs there are
            Copy over ONE COPY of the rad files to each VM
            Divide the number of hourly directories by the number of vm's
            and send each group of directories to the correct VM
"""
# Get the count and IP addresses of the currently assigned VM's
vm_count = GET_VMCount()
vm_IP_List = GET_VMIP()

# Get number of sim hours that will go to each VM
directory_contents = sorted([f for f in os.listdir(Local_Main_Directory) if not f.startswith('.')], key=lambda f: f.lower())
chunk_size = math.ceil(len(directory_contents) / vm_count)

# Look more into how this works, but this will split the folder names into even chunks based on the number of VMs
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
divideIntoMachineGroups = [directory_contents[i:i + chunk_size] for i in range(0, len(directory_contents), chunk_size)]

sms = sms.SMS()
for i in range(vm_count):
    Folders_To_Send = divideIntoMachineGroups[i]
    IP = vm_IP_List[i]
    print("Machine " + str(i))
    login = Login()
    ssh = pf_ssh(IP,22, login.ADMIN_NAME, login.ADMIN_PSWD)
    ssh.sendCommand("mkdir new")
    for radfile in Rad_Files_For_Transfer:
        original_file_path = os.path.abspath(radfile)
        destination_file_path = Azure_Main_Directory + r"/" + os.path.split(original_file_path)[1]
        ssh.copyfilesSCP(IP,22,login.ADMIN_NAME,login.ADMIN_PSWD,original_file_path,destination_file_path)

    # Iterate through each folder and send the contents
    for folder in Folders_To_Send:
        folderobject = os.path.join(Local_Main_Directory,folder)
        if os.path.isdir(folderobject):
            print("CURRENT FOLDER IS: " + folder)
        for root,dirs,files in os.walk(os.path.join(Local_Main_Directory,folder)):
            for file in files:
                if not file == ".DS_Store" and not file.endswith(".rad"):
                    print(file)
                    original_file_path = os.path.join(root,file)
                    ssh.sendCommand("mkdir ./new/" + folder)
                    destination_file_path = Azure_Main_Directory + r"/" + folder + r"/" + file
                    ssh.copyfilesSCP(IP,22,login.ADMIN_NAME,login.ADMIN_PSWD,original_file_path,destination_file_path)
        print()

    sms.DGPfilesCopiedToCloud(i,login)
    print("\n\n")
