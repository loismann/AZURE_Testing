import subprocess
import os
import time
from collections import defaultdict

##### Functions

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

# This actuall runs the batch files
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

##### Run Code
if __name__ == "__main__":
    # Get the main directory we're working in
    Main_Directory = "/home/pferrer/new"
    # Make the directory fully R/W
    # os.chmod(Main_Directory,777)
    # Find the different inputs for running the batch files
    for root, dirs, files in os.walk(os.path.abspath(Main_Directory)):
        for folder in dirs:
            current_folder = os.path.join(Main_Directory,folder)
            os.chdir(current_folder)
            print(os.getcwd())
            params = FIND_BatchFileTypes(current_folder)
            print(params)
            print()
            # Deep Breath.... Run all the batch files
            RUN_BatchFiles(params.get('initBatchFileName'),params.get('supportingBatchFiles'), params.get('pcompBatchFile'))

