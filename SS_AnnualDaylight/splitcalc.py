# coding=utf-8
"""
Split the sunlight coefficients file to over 1095 chunks, each containing 100 lines (each line represents a point).
There are 8760 RGB triplets within each line.
The total in this way will add upto 109453 points, with the last line having 53 points.

Step two involves running dctimestep. At any time 16 processes of dctimestep will be run and this way all the 219 files
will be accounted for. Then these files will be joined together into a single illuminance file to do the RGB triplet
calculation.

I had trouble loading these files into rmtxop to do the triplet calculation, so I decided to write a python routine
to do this.
"""


from __future__ import print_function
import os
import sys
import multiprocessing as mp
import random

headerString ="""#?RADIANCE
oconv black.rad materials.rad sceneASE.rad skies/suns.rad
rcontrib -I+ -ab 1 -y 109453 -n 16 -ad 256 -lw 1.0e-3 -dc 1 -dt 0 -dj 0 -faa -e MF:6 -f reinhart.cal -b rbin -bn Nrbins -m solar
SOFTWARE= RADIANCE 5.1a lastmod Thu Aug 10 21:33:09 UTC 2017 by hksline on cld-envsim-01
CAPDATE= 2017:08:28 19:19:18
GMT= 2017:08:28 19:19:18
NCOMP=3
NROWS=%s
NCOLS=5186
FORMAT=ascii

"""

def splitBigMatrixFile():
    count = 1
    fileCounter = 1
    lineList = []
    with open('matrices/ASE.mtx') as matrixData:
        for idx,lines in enumerate(matrixData):
            if lines.strip():
                try:
                    lineSplit = lines.split()
                    lineSplit = map(float,lineSplit)
                    lineList.append(lines.strip())
                    if len(lineList)>99:
                        with open('matrices/ASE/%04d.mtx'%fileCounter,'w') as matrixWrite:
                            matrixWrite.write(headerString%len(lineList))
                            matrixWrite.write("\n".join(lineList))
                            fileCounter+=1
                            lineList=[]
                except ValueError:
                    pass

            else:
                    print(lines.strip())
        else:
            with open('matrices/ASE/%04d.mtx' % fileCounter, 'w') as matrixWrite:
                matrixWrite.write(headerString % len(lineList))
                matrixWrite.write("\n".join(lineList))


def runCommand(val):
        print("The val is %s"%val)
        os.system(val)

def matrixMultiplication():
    matrixFiles = []
    commands = []
    skyVector = "skyvectors/SFOsunM6.smx"

    for idx,fileName in enumerate(sorted(os.listdir('matrices/ASE'))):
        matrixName = os.path.join('matrices/ASE',fileName)
        resultName = 'results/ASE/%04d.tmp'%idx
        matrixFiles.append(matrixName)
        commands.append('dctimestep %s %s > %s'%(matrixName,skyVector,resultName))

    someFile = matrixFiles[random.randint(0,1042)]
    #Pick a random file and check if it exists.
    assert os.path.exists(matrixFiles[random.randint(0,1042)])

    return commands

headerStringIll="""#?RADIANCE
dctimestep matrices/ASE/0001.mtx skyVectors/SFOM6.smx
CAPDATE= 2017:08:29 18:15:59
GMT= 2017:08:29 18:15:59
NROWS=104157
NCOLS=8760
NCOMP=1
FORMAT=ascii

"""

def extractIlluminance():
    # This takes the split up files from results/ASE and loads/compresses them
    resultName = 'results/ASE'

    with open('results/ASEIll.ill','w') as aseFile:
        print(headerStringIll,file=aseFile)
        for fileIdx,fileName in enumerate(sorted(os.listdir(resultName))):
            fileName = os.path.join(resultName,fileName)
            with open(fileName) as partialData:
                for idx,lines in enumerate(partialData):
                    if lines.strip():
                        try:
                            lineSplit = lines.split()
                            lineSplit = map(float, lineSplit)
                            data = [lineSplit[idx * 3:idx * 3 + 3] for idx in xrange(8760)]
                            data = [int(val[0] * 47.4 + val[1] * 119.9 + val[2] * 11.6) for val in data]
                            data = "\t".join(map(str, data))
                            print(data, file=aseFile)
                        except ValueError:
                            pass
            print(fileName)


def compressIlluminance(InputFile,OutputFile = None):
    """
    For sDA: This function takes an illuminance file with RGB triplets and compresses it to a file containing integers for
    illuminance.  This will allow us to load a file into memory that otherwise would be to large.
    :return:
    """
    OutputFile = OutputFile or os.path.splitext(InputFile)[0] + "C" + os.path.splitext(InputFile)[1]

    with open(OutputFile,'w') as OutputData:
        print(headerStringIll,file= OutputData)
        with open(InputFile) as partialData:
                for idx,lines in enumerate(partialData):
                    if lines.strip():
                        try:
                            lineSplit = lines.split()
                            lineSplit = map(float, lineSplit)
                            data = [lineSplit[idx * 3:idx * 3 + 3] for idx in xrange(8760)]
                            #https://en.wikipedia.org/wiki/Luminosity_function
                            data = [int(val[0] * 47.4 + val[1] * 119.9 + val[2] * 11.6) for val in data]
                            data = "\t".join(map(str, data))
                            print(data, file=OutputData)
                        except ValueError:
                            print(lines)




if __name__ == "__main__":
    pass
    # if running this file for the first time, run all these commands at once
    #Split the big daylight matrix file into multiple chunks.
    # splitBigMatrixFile()

    #Get the list of commands to be executed with dctimestep.
    # commands = matrixMultiplication()

    #Run dctimesteps, 16 at at time.
    # pools = mp.Pool(processes=16)
    # pools.map(runCommand, commands)

    #Convert results from dctimesteps into illuminance, combine the results into one file.
    # extractIlluminance()

