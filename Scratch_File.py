

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


def bat_to_sh(file_path):
    """Convert a honeybee .bat file to .sh file.

    WARNING: This is a very simple function and doesn't handle any edge cases.
    """
    sh_file = file_path[:-4] + '.sh'
    with open(file_path, 'rb') as inf, open(sh_file, 'wb') as outf:
        outf.write('#!/usr/bin/env bash\n\n')
        for line in inf:
            # pass the path lines, etc to get to the commands
            if line.strip():
                continue
            else:
                break

        for line in inf:
            if line.startswith('echo'):
                continue
            # replace c:\radiance\bin and also chanege \\ to /
            modified_line = line.replace('c:\\radiance\\bin\\', '').replace('\\', '/')
            outf.write(modified_line)

    print('bash file is created at:\n\t%s' % sh_file)
    return sh_file


# if __name__ == '__main__':
#     file_path = \
#         r'C:\ladybug\170914_DA_Study_with_DC\gridbased_daylightcoeff\commands.bat'
#     bash_file_path = bat_to_sh(file_path)