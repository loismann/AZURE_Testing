import subprocess
import os
import time
from collections import defaultdict
import shutil
import zipfile

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
        pass
        # print("Something went wrong: %s" % str(e))

# This actuall runs the batch files
def RUN_BatchFiles(initBatchFileName, batchFileNames, pcompBatchFile, waitingTime=0.5, runInBackground=False):
    excecuteBatchFiles([initBatchFileName], maxPRuns=1, shell=runInBackground, waitingTime=waitingTime)
    excecuteBatchFiles(batchFileNames, maxPRuns=len(batchFileNames), shell=runInBackground, waitingTime=waitingTime)

    if pcompBatchFile != "":
        os.system(pcompBatchFile)  # put all the files together

# Strip the files...again
def SarithFileStrip(fname):
    if fname.endswith(".sh"):
        name, ext = os.path.splitext(fname)
        newname = name + "new." + ext
        with open(fname) as f, open(newname, "w") as f2:
            for lines in f:
                if lines.strip():
                    f2.write(lines.strip() + '\n')
                # print(list(lines))

        os.rename(newname, fname)
        # print("file stripped and renamed")
        # print("found a shell file")
    else:
        print("function at least ran")

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
                SarithFileStrip(file_path)
                os.chmod(file_path, 0o777)
                batchFile_parameters["pcompBatchFile"] = file_path

            # If it runs across an init file, add it to the dictionary
            elif file_path.endswith(".sh") and "Init" in file_path:
                # print("found the init file")
                SarithFileStrip(file_path)
                os.chmod(file_path,0o777)
                batchFile_parameters["initBatchFileName"] = file_path

            # When it runs across any other sh files in the directory add them too
            elif file_path.endswith(".sh"):
                # print("found a supporting file")
                SarithFileStrip(file_path)
                os.chmod(file_path, 0o777)
                batchFile_parameters["supportingBatchFiles"].append(file_path)

    return batchFile_parameters

##### Run Code
if __name__ == "__main__":
    # Get the main directory we're working in
    Main_Directory = "/home/pferrer/new"
    # Make the directory fully R/W
    # os.chmod(Main_Directory,777)

    # Unzip the working files
    for root, dir, files in os.walk(Main_Directory):
        for file in files:
            if str(file).endswith('.zip'):
                print('found a zip file')
                destination_file_path = os.path.join(Main_Directory, file)
        # Unzip the working files to the Main Directory
    with zipfile.ZipFile(destination_file_path, 'r') as zip_ref:
        zip_ref.extractall(Main_Directory)

    os.remove(destination_file_path)
    print("launched 'HKS_LaunchDGP' file remotely and unzipped files")



    FIND_BatchFileTypes(Main_Directory)
    # Find the different inputs for running the batch files
    print("Running Sims Remotely...")
    for root, dirs, files in os.walk(Main_Directory):
        if 'imageBasedSimulation' in root:
            os.chdir(root)
            # print(os.getcwd())
            params = FIND_BatchFileTypes(root)
            # Deep Breath.... Run all the batch files
            RUN_BatchFiles(params.get('initBatchFileName'),params.get('supportingBatchFiles'), params.get('pcompBatchFile'))
    # # Collect the results of the sims
    collectedHDRdirectory = Main_Directory + "/" + "CollectedHDRfiles"

    # Maybe add something here to delete a previously existing copy of the directory
    # This would prevent me having to manually delete the existing directory before running a new test
    if os.path.exists(collectedHDRdirectory):
        shutil.rmtree(collectedHDRdirectory)
    #
    #
    print("Moving the HDR files into a single folder")
    os.mkdir(collectedHDRdirectory)
    print("Moving finished HDR files to single location ")
    hdr_list = []
    for root, dirs, files in os.walk(Main_Directory):
        counter = 0
        for file in files:
            if file.endswith(".HDR") and file[-5] != "0":
                collectedLocation = os.path.join(collectedHDRdirectory,file)
                nestedlocation = os.path.join(root, file)
                hdr_list.append(nestedlocation)
    #
    for file in hdr_list:
        base = os.path.basename(file)
        root = collectedHDRdirectory
        newlocaction = os.path.join(root,base)
        shutil.copy(file,newlocaction)
    time.sleep(3)
    print("zipping HDR files")
    output_filename = Main_Directory + "/" + "finishedHDRs"
    print(output_filename)
    print(collectedHDRdirectory)
    shutil.make_archive(output_filename,"zip",collectedHDRdirectory)
    #
    print("waiting until files all zipped up")
    time.sleep(5)
