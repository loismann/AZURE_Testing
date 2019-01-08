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
    print("This is how many files we're transferring: " + str(len(filesForRemoteTransfer)))
    os.chdir(Local_Main_Directory_AGBD)
    with zipfile.ZipFile("Transfer" + ".zip", "w") as zip:
        for file in filesForRemoteTransfer:
            zip.write(file,os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)


# This performs all operations to get the files over to azure and then run them
# THIS WAS COPIED FROM THE DGP ANALYSIS FILES.  REMOVE THIS MESSAGE WHEN PROPERLY MODIFIED TO RUN ANNUAL GRID BASED DAYLIGHT CALCS
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



###############################################  DEFINE THE MAIN FUNCTION  ###########################################

def main(Local_Main_Directory_AGBD):
    # ALL MULTITHREADING LOGIC TAKES PLACE HERE.  EACH OF THE FUNCTIONS REPRESENTS OPERATION ON A SINGLE ELEMENT
    filesForRemoteTransfer = getFilesForTransfer(Local_Main_Directory_AGBD)
    zipFiles(Local_Main_Directory_AGBD,filesForRemoteTransfer)