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
# import HELPERS.HELPER_ResetTestFiles as reset
import zipfile
from pathlib import Path
import random


##########################################  DEFINE THE HELPER FUNCTIONs  ###############################################

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
        path = os.path.join(scriptdirectory, "Local_IP_Addresses.py")
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


# This function will identify the base files that will be transferred to the cloud
def getFilesForTransfer(Local_Main_Directory_AGBD):
    Files_For_Transfer = []
    for root, dirs, files in os.walk(os.path.abspath(Local_Main_Directory_AGBD)):
        for file in files:
            file_path = os.path.join(root, file)

            if file_path.endswith(".rad") or file_path.endswith(".pts"):
                Files_For_Transfer.append(file_path)

    return Files_For_Transfer


# Zip the identified files
def zipFiles(Local_Main_Directory_AGBD,filesForRemoteTransfer):
    # print("This is how many files we're transferring: " + str(len(filesForRemoteTransfer)))
    os.chdir(Local_Main_Directory_AGBD)
    with zipfile.ZipFile("Transfer" + ".zip", "w") as zip:
        for file in filesForRemoteTransfer:
            zip.write(file,os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)

    zipped_file = None
    for file in os.listdir(os.getcwd()):
        if file.endswith(".zip"):
            zipped_file = file

    return os.path.abspath(zipped_file)

# This performs all operations to get the files over to azure and then run them
# THIS WAS COPIED FROM THE DGP ANALYSIS FILES.  REMOVE THIS MESSAGE WHEN PROPERLY MODIFIED TO RUN ANNUAL GRID BASED DAYLIGHT CALCS
def sendFilesToAzureAndLaunch(Azure_Main_Directory,
                              vm_IP_List,
                              zipFilesForRemoteTransfer,
                              ):

    sleepTime = random.randint(0,2)
    print("randomly sleeping for " + str(sleepTime) + " seconds before beginning file transfer")
    time.sleep(sleepTime)
    #
    IP = vm_IP_List
    login = Login()
    ssh = pf_ssh(IP, 22, login.ADMIN_NAME, login.ADMIN_PSWD)
    print("Removing all folders in the 'new' directory to start fresh")
    ssh.sendCommand("rm -r new")
    sms_instance = sms.SMS()

    # Might need to clear out the home directory first to help with testing:
    # Check and see if the "new" folder exists
    # if it does, delete it and then make it again
    # print(IP)
    # print(Azure_Main_Directory)

    ssh.sendCommand("mkdir new")
    original_file_path = zipFilesForRemoteTransfer
    destination_file_path = Azure_Main_Directory + r"/" + os.path.split(original_file_path)[1]
    ssh.copyfilesSCP(IP, 22, login.ADMIN_NAME, login.ADMIN_PSWD, original_file_path, destination_file_path)
    #
    #
    # # Copy the "HKS_LaunchDGP.py" file to the remote system
    # original_file_path = os.path.join(login.Local_Repo_Directory,HKS_LaunchDGP)
    # destination_file_path = Azure_Main_Directory + "/" + HKS_LaunchDGP
    # ssh.copyfilesSCP(IP, 22, login.ADMIN_NAME, login.ADMIN_PSWD, original_file_path, destination_file_path)
    # print(destination_file_path + " Copied to Azure")
    #
    #
    # # LAUNCH SIMULATIONS
    # ssh.sendCommand("python " + destination_file_path)
    # print("Simulations launched on Machine")
    # # sms_instance.SimulationsStarted(i, login)



###############################################  DEFINE THE MAIN FUNCTION  ###########################################

def main(Local_Main_Directory_AGBD):
    # This location is fixed and should not change for any cloud based sims using the LINE image template
    Azure_Main_Directory = "/home/pferrer/new"

    # Identify which files are going to be sent to azure
    filesForRemoteTransfer = getFilesForTransfer(Local_Main_Directory_AGBD)

    # zip up the files
    zippedfile = zipFiles(Local_Main_Directory_AGBD,filesForRemoteTransfer)

    # Get the count and IP addresses of the currently assigned VM's
    # vm_count = GET_VMCount()
    vm_IP_List = GET_VMIP()
    sms_main = sms.SMS()
    login_main = Login()

    # send all files to azure
    sendFilesToAzureAndLaunch(Azure_Main_Directory, vm_IP_List[0], zippedfile)