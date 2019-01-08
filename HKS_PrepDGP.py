import subprocess
import os
import time
import math
from collections import defaultdict
from HELPERS.HELPER_SSH import pf_ssh
import shutil
from HELPERS.HELPER_Login_Info import Login
import HELPERS.HELPER_SMS as sms
import threading
import multiprocessing
import paramiko
from stat import S_ISDIR
import HELPERS.HELPER_ResetTestFiles as reset
import zipfile
from pathlib import Path
import random


###### Important Global Variables #########
HKS_LaunchDGP = r'HKS_LaunchDGP.py'



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
                                # print("removed the 'del' command")
                                replaced.append("rm")
                            elif ".rad" and "material" in segment:
                                # print("Found the Material.rad file")
                                redirection = "../../Materials.rad"
                                replaced.append(redirection)
                            elif ".rad" in segment and "material" not in segment:
                                # print("Found the Object.rad file")
                                redirection = "../../Objects.rad"
                                replaced.append(redirection)
                            elif ".sky" in segment:
                                # print("Found a sky file")
                                redirection = os.path.split(segment)[1]
                                # print(redirection)
                                replaced.append(redirection)
                            else:
                                replaced.append(segment)
                        new_line = " ".join(replaced)
                        outfile.write(new_line + '\n')
            outfile.close()

    # This removes carriage returns (thanks sarith)
    # NEED TO CHECK IF THIS IS ACTUALLY RUNNING.  I DONT THINK IT IS
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
                        print("this came from sarith's function")
                os.rename(newname, fname)

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

# Need to turn the "prepare file transfer function into two functions.
# The first will be a simple function that sets the rad files to be copied to each machine
# The second one will be a function that runs the bat to sh process in parallel.
def radFilesForTransfer(Local_Main_Directory):
    """
    This Needs to be run once as a single threaded operation.  This function will set the project rad files outside
    the main directory.  Once this has been run you can then run the multi-threaded function that will run the bat to
    sh conversion and delete the rad files
    :param Local_Main_Directory:
    :return:
    """
    mat_rad = None
    object_rad = None
    Rad_Files_For_Transfer = []

    if not os.path.isfile(os.path.join(Local_Main_Directory, "Materials.rad")):
        for root, dirs, files in os.walk(os.path.abspath(Local_Main_Directory)):
            if not os.path.isfile(os.path.join(root, "Materials.rad")):
                for file in files:
                    file_path = os.path.join(root, file)
                    # This will set the rad variables to the first copy of the rad files encountered
                    if (mat_rad == None or object_rad == None) and file_path.endswith(".rad"):
                        if "material" in file_path:
                            mat_rad = file_path
                        else:
                            object_rad = file_path
            else:
                pass

        if mat_rad:
            moved1 = os.path.join(Local_Main_Directory, "Materials.rad")
            moved2 = os.path.join(Local_Main_Directory, "Objects.rad")

            os.rename(shutil.move(mat_rad, Local_Main_Directory), moved1)
            os.rename(shutil.move(object_rad, Local_Main_Directory), moved2)
            Rad_Files_For_Transfer.append(moved1)
            Rad_Files_For_Transfer.append(moved2)

        else:
            pass

    else:
        # print("file exists")
        pass


    return Rad_Files_For_Transfer

# This has now been modified to return a list of folders instead of a dictionary.  The list works well with the "pool"
# option of multithreading
# This returns a dictionary that can be used to multithread the bat to sh process
def getParallelDictionaryForFilePrep(Local_Main_Directory):
    filePrepDict = {}
    filePrepList = []
    hourlyFolders = []
    counter = 0
    for root, dirs, files in os.walk(os.path.abspath(Local_Main_Directory)):
        if "image" not in root and "00" in root:
            filePrepList.append(root)
            # filePrepDict[counter] = root
            # print(root)
            counter +=1

    return filePrepList

# This will convert batch files and strip/ rad files
#  THIS IS THE NEW WORK IN PROGRESS and is now set to accept a single folder path
def prepareFileTransfer(folder_path):
    """
    As an input, this function needs a dictionary that will determine how many processes to run this operation on
    the dictionary will have an index number as a "key" and a list of folder paths representing an even subdivision of the
    hourly calculation as the "value"
    :param Local_Main_Directory:
    :return:
    """
    # THIS FUNCTION ABSOLUTELY NEEDS TO BE MULTI-THREADED
    # These variables will hold a copy of the rad files

    convert = Convert()
    # print("Running bat/sh File Conversion on sim-hour: ")
    # walk through the folder paths to find the file path

    for root, dirs, files in (os.walk(folder_path)):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(".bat"):
                convert.bat_to_sh_DGP(file_path)
                convert.sarithFixFile(folder_path)
                os.remove(file_path)
            elif file_path.endswith(".rad"):
                os.remove(file_path)


# This performs all operations to get the files over to azure and then run them
def sendFilesToAzureAndLaunch(Azure_Main_Directory,
                              vm_IP_List,
                              zipFilesForRemoteTransfer,
                              ):

    sleepTime = random.randint(0,10)
    print("randomly sleeping for " + str(sleepTime) + " seconds before beginning file transfer")
    time.sleep(sleepTime)

    IP = vm_IP_List
    login = Login()
    ssh = pf_ssh(IP, 22, login.ADMIN_NAME, login.ADMIN_PSWD)
    print("Removing all folders in the 'new' directory to start fresh")
    ssh.sendCommand("rm -r new")
    sms_instance = sms.SMS()

    # Might need to clear out the home directory first to help with testing:
    # Check and see if the "new" folder exists
    # if it does, delete it and then make it again
    print(IP)
    print(Azure_Main_Directory)

    ssh.sendCommand("mkdir new")
    original_file_path = zipFilesForRemoteTransfer
    destination_file_path = Azure_Main_Directory + r"/" + os.path.split(original_file_path)[1]
    ssh.copyfilesSCP(IP, 22, login.ADMIN_NAME, login.ADMIN_PSWD, original_file_path, destination_file_path)


    # Copy the "HKS_LaunchDGP.py" file to the remote system
    original_file_path = os.path.join(login.Local_Repo_Directory,HKS_LaunchDGP)
    destination_file_path = Azure_Main_Directory + "/" + HKS_LaunchDGP
    ssh.copyfilesSCP(IP, 22, login.ADMIN_NAME, login.ADMIN_PSWD, original_file_path, destination_file_path)
    print(destination_file_path + " Copied to Azure")


    # LAUNCH SIMULATIONS
    ssh.sendCommand("python " + destination_file_path)
    print("Simulations launched on Machine")
    # sms_instance.SimulationsStarted(i, login)

def sftp_walk(remotepath,sftp):
    path=remotepath
    files=[]
    folders=[]
    for f in sftp.listdir_attr(remotepath):
        if S_ISDIR(f.st_mode):
            folders.append(f.filename)
        else:
            files.append(f.filename)
    if files:
        yield path, files
    for folder in folders:
        new_path=os.path.join(remotepath,folder)
        for x in sftp_walk(new_path,sftp):
            yield x

def collectHDRfiles(Azure_Main_Directory,vm_IP_List,i,Local_HDR_Directory):
    IP = vm_IP_List[i]
    login = Login()
    transport = paramiko.Transport((IP, 22))
    transport.connect(username=login.ADMIN_NAME, password=login.ADMIN_PSWD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    # print(sftp_walk(Azure_Main_Directory,sftp))
    sftp.get(Azure_Main_Directory + "/finishedHDRs.zip",Local_HDR_Directory + "\\finishedHDRs_Machine_" + str(i) + ".zip")
    print(Azure_Main_Directory + "/finishedHDRs.zip")
        # print(files)
    # #
    #         # if os.path.split(file)[1] ==
    #         if file.endswith(".HDR") and file[-5] != "0":
    #             # print(file)
    #             #sftp.get(remote, local) line for dowloading.
    #             sftp.get(os.path.join(os.path.join(path,file)), Local_HDR_Directory + file)
    #             # print("/Users/paulferrer/Desktop/TEST/" + file)

def zipFilesAndDelete(Local_Main_Directory, divideIntoMachineGroups, Rad_Files_For_Transfer):
    # initializing empty file paths list
    original_file_paths = []
    zip_file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(Local_Main_Directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            if "rad" not in filename:
                filepath = os.path.join(root, filename)
                original_file_paths.append(filepath)
                # Here is how i'm getting a location that keeps the local structure but not the original structure
                # https://stackoverflow.com/questions/27844088/python-get-directory-two-levels-up
                trimmed_pathsection = list(Path(filepath).parts[5:])
                zip_file_paths.append(os.path.join(*trimmed_pathsection))

    print("This is how many files we're transferring: " + str(len(original_file_paths)))
    list_index_tracker = 0

    for i in range(len(divideIntoMachineGroups)):
        group = divideIntoMachineGroups[i]
        with zipfile.ZipFile("hours_" + str(i) + ".zip", "a") as zip:
            for j in range(len(group)*5):
                zip.write(original_file_paths[list_index_tracker],zip_file_paths[list_index_tracker])
                list_index_tracker += 1

            # Delete all the folders to clean up the directory
            for j in range(len(group)):
                shutil.rmtree(os.path.normpath(group[j]))

            # Add the rad files to the zip file
            for file in Rad_Files_For_Transfer:
                zip.write(file,os.path.basename(file))

    # Delete the Rad files
    for file in Rad_Files_For_Transfer:
        os.remove(file)




###############################################  DEFINE THE MAIN FUNCTION  ###########################################

def main(Local_Main_Directory,Local_HDR_Directory):
    # ALL MULTITHREADING LOGIC TAKES PLACE HERE.  EACH OF THE FUNCTIONS REPRESENTS OPERATION ON A SINGLE ELEMENT


    # This location is fixed and should not change for any cloud based sims using the LINE image template
    Azure_Main_Directory = "/home/pferrer/new"


    # Walk the Directory and Convert the batch files
    # At the same time, isolate a copy of the rad files outside the folder structure, and then
    # delete all the other rad files encountered in the folders

    # Run the HELPER_ResetTestFiles.py Script
    print("Copying files to test directory...")

    # THIS DELETES ALL FILESS/FOLDERS IN THE TEST DIRECTORY AND THEN PUTS IN A FRESH COPY
    # At this point you cant really turn off this function, it will mess up the hourly counting of the other functions
    reset.main()

    print("All files copied to local directory and ready to process")
    Rad_Files_For_Transfer = radFilesForTransfer(Local_Main_Directory)
    hourly_list = getParallelDictionaryForFilePrep(Local_Main_Directory)


    # "Pool" MULTITHREADED VERSION OF PREPARE FOR TRANSFER
    print("Preparing files for transfer...")

    hourcount = 0
    for item in os.listdir(Local_Main_Directory):
        if os.path.isdir(os.path.join(Local_Main_Directory,item)):
            hourcount += 1

    p_sendAndRun = multiprocessing.Pool(multiprocessing.cpu_count())
    result=p_sendAndRun.map(prepareFileTransfer, hourly_list)
    p_sendAndRun.close()
    p_sendAndRun.join()
    print("Files prepped for transfer")



    # Get the count and IP addresses of the currently assigned VM's
    vm_count = GET_VMCount()
    vm_IP_List = GET_VMIP()
    sms_main = sms.SMS()
    login_main = Login()
    # # print(type(login_main))
    # # Get number of sim hours that will go to each VM
    directory_contents = sorted([f for f in os.listdir(Local_Main_Directory) if not f.endswith('.rad')], key=lambda f: f.lower())
    chunk_size = math.ceil(len(directory_contents) / vm_count)
    #
    # # Look more into how this works, but this will split the folder names into even chunks based on the number of VMs
    # # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    divideIntoMachineGroups = [directory_contents[i:i + chunk_size] for i in range(0, len(directory_contents), chunk_size)]


    # print("\nThis is now the PrepDGP file")
    # print("Number of VMs detected: " + str(vm_count))
    # print(divideIntoMachineGroups)
    # for grouping in divideIntoMachineGroups:
    #     print(len(grouping))


    # THIS IS GOING TO TEST OUT ADDING ALL THESE FOLDERS INTO ARCHIVES.  IN A QUANTITY THAT MATCHES
    # THE NUMBER OF VMs CURRENTLY IN USE
    # Change the Current Working directory to the Local Main Directory
    os.chdir(Local_Main_Directory)
    print("Generating Zip Files...")
    zipFilesAndDelete(Local_Main_Directory, divideIntoMachineGroups, Rad_Files_For_Transfer)

    # End of the timer
    # elapsed_time = int(time.time() - start_time)
    # print("Elapsed Time to prep and Zip all files: " + str(elapsed_time) + " seconds")

    # Get a list of the zip files to send
    zipFilesForRemoteTransfer = []
    for item in os.listdir(Local_Main_Directory):
        zipFilesForRemoteTransfer.append(os.path.join(Local_Main_Directory,item))

    # print(len(vm_IP_List))
    # print(len(zipFilesForRemoteTransfer))
    print(len(vm_IP_List))


    # Multithreaded(processing) send zip to remote machines and run
    jobs = []
    print("now running 'processing' multithreading of send to azure and run...")
    for i in range(len(zipFilesForRemoteTransfer)):
        p = multiprocessing.Process(target=sendFilesToAzureAndLaunch,
                                    args=(Azure_Main_Directory,
                                          vm_IP_List[i],
                                          zipFilesForRemoteTransfer[i]))
        jobs.append(p)
        p.start()

    for job in jobs:
        job.join()

    # # Multithreaded(starmap) send zip files to remote machines
    # print('Running Starmapped "SendToAzureAndRun" Function')
    # p_sendRemote = multiprocessing.Pool(multiprocessing.cpu_count()-1)
    # starmap_tuple = []
    # for i in range(len(zipFilesForRemoteTransfer)):
    #     starmap_tuple.append((Azure_Main_Directory,vm_IP_List[i],zipFilesForRemoteTransfer[i]))
    # result = p_sendRemote.starmap(sendFilesToAzureAndLaunch,starmap_tuple)
    # p_sendRemote.close()
    # p_sendRemote.join()
    # print("Files prepped for transfer")
    # # sms_main.SimulationsComplete(login_main)


    ##### This is now moving to the "Launch DGP py file" -  things are now running remotely


    ## The simulations are done, and we're moving back to local processing:
    # Multithreaded version of Collect HDR
    print("Running Multithreaded Collect HDR")
    jobs_CollectHDR = []
    for i in range(len(zipFilesForRemoteTransfer)):
        print("Collecting HDR files from machine: " + str(i + 1))
        p_CollectHDR = multiprocessing.Process(target=collectHDRfiles,
                                    args=(Azure_Main_Directory,
                                          vm_IP_List,
                                          i,
                                          Local_HDR_Directory))
        jobs_CollectHDR.append(p_CollectHDR)
        p_CollectHDR.start()


    for job in jobs_CollectHDR:
        job.join()

    sms_main.HDRsCopied(login_main)
    print("All Simulations complete\n")

    print("HDR files copied back to local machine\n")

    # last step! Unzip the HDR files and delete the zip containers
    for root, dir, files in os.walk(Local_HDR_Directory):
        for file in files:
            if str(file).endswith('.zip'):
                print('found a zip file')
                destination_file_path = os.path.join(Local_HDR_Directory, file)
                # Unzip the working files to the Main Directory
                with zipfile.ZipFile(destination_file_path, 'r') as zip_ref:
                    zip_ref.extractall(Local_HDR_Directory)
                os.remove(destination_file_path)
    print("ALL DONE!!!")



# For testing this individual file:
# Local_Main_Directory = r"C:\Users\pferrer\Desktop\test"
# Local_Repo_Directory = r"C:\Users\pferrer\PycharmProjects\AZURE_Testing"
# Local_HDR_Directory = r"C:\Users\pferrer\Desktop\TEST_CopiedHDRfiles"
# Local_Main_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles"
# if __name__ == "__main__":
#     main(Local_Main_Directory,Local_HDR_Directory)
#
# # radFilesForTransfer(Local_Main_Directory)
# dict = getParallelDictionaryForFilePrep(Local_Main_Directory)
# print(dict)
# prepareFileTransfer(dict,1)
