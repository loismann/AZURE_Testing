import os
import warnings
import sys
sys.path.append("/home/pferrer/hksSim")
from results.dayIll import Dayill
print Dayill
from splitcalc import compressIlluminance

# This makes the octree.  adds in the black material, the all black scene for the leak test and redirects everything to
# an octree
# os.system("oconv black.rad sceneblack_leak.rad sky.rad > leakcheck.oct")

# This is running the leak test
# os.system("rtrace -I+ -ab 0 -aa 0.2 -ar 1024 -ad 2048 -dc 1 -dt 0 -dj 1 leakcheck.oct < finalpoints.txt > leakresults.txt")

# with open("leakresults.txt") as leakfile:
#     for idx,lines in enumerate(leakfile):
#         try:
#             if lines.strip():
#                 sumresult = sum(map(float, lines.strip().split()))
#                 if sumresult > 0:
#                     print(sumresult,idx)
#         except ValueError:
#             pass
#     print idx


##The number of suns considered in this case are the same as that propsed in the DDS Model from 2008. Higher accuracy may be obtained by considering a larger number of suns through MF:5, MF:6 etc.

####################################################### ALL ASE #################################################

# Calculate the number of points in the file
def calcpoints(pointsfilepath):
    counter = 0
    with open(pointsfilepath) as pointsdata:
        for lines in pointsdata:
            if lines.strip():
                counter += 1
            else:
                warnings.warn("White Space Detected!!!!!")
    return counter


linelength = calcpoints("points.pts")
print linelength


# Step 1: Create sun coefficents
def create_suncoef():

    # ##Create sun primitive definition for solar calculations.
    os.system('echo "void light solar 0 0 3 1e6 1e6 1e6" > skies/suns.rad')
    # ##Create solar discs and corresponding modifiers for 5165 suns corresponding to a Reinhart MF:6 subdivision.
    #
    # ##Formula for MF = 144*MF*MF+1
    os.system("cnt 5165 | rcalc -e MF:6 -f reinsrc.cal -e Rbin=recno -o 'solar source sun 0 0 4 ${Dx} ${Dy} ${Dz} 0.533' >> skies/suns.rad")

    # ##Create an octree BLACK OCTREE, shading device with proxy BSDFs and solar discs.
    os.system("oconv -f blackscene.rad skies/suns.rad > octrees/ASE.oct")


    # ##Calculate illuminance sun coefficients for illuminance calculations. (Ray tracing)
    # -faf will make a binary file (smaller file size)  changing this to -faa will turn this into an ascii file
    os.system("rcontrib -I+ -ab 1 -y %s -n 16 -ad 256 -lw 1.0e-3 -dc 1 -dt 0 -dj 0 -faa -e MF:6"
              " -f reinhart.cal -b rbin -bn Nrbins -m solar octrees/ASE.oct"
              " < points.pts > matrices/ASE.mtx"%linelength)

# Step 2: Create sun matrix
# make sure all the "MF" numbers match up
def create_sunmatrix():
    #os.system("epw2wea assets/CA_SAN-FRANCISCO-IAP_724940_TY3.epw assets/CA_SAN-FRANCISCO-IAP_724940_TY3.wea")
    #os.system("gendaymtx -5 0.533 -d -m 6 -r -28 assets/CA_SAN-FRANCISCO-IAP_724940_TY3.wea > skyvectors/SFOsunM6.smx")
    # Step 3:Matrix Multiplication(rmtxop is the command) - Run the "splitcalc".py file
    # make sure that the number of files to split into matches the number of points in the model
    # basically need to create groups of 100 points
    # this last command is only for "small" files
    #os.system("dctimestep matrices/ASE.mtx skyvectors/SFOsunM6.smx | rmtxop -fa -t -c 47.4 119.9 11.6 - > results/ASE.ill")
    pass

 #Run Commands
#create_suncoef()
#create_sunmatrix()

# calculate ase
import time
def calc_ASE(ASEIll):
    #
    # os.system("getinfo %s > ASEresultssize.txt"%ASEIll)
    # with open("ASEresultssize.txt") as ASEdata:
    #     nrows = None
    #     for lines in ASEdata:
    #         lines = lines.strip()
    #         if lines.startswith("NROWS"):
    #             text,number = lines.split("=")
    #             number = int(number)
    #             if number != 8760:
    #                 print("transposing results matrix file at %s"%time.ctime())
    #                 os.system("rmtxop -t %s > results/ASEIllt.ill"%ASEIll)
    #                 ASEIll = "results/ASEIllt.ill"

    x = Dayill(ASEIll, "points.pts", convertFromRadiance=True,
               weaFile="assets/CA_SAN-FRANCISCO-IAP_724940_TY3.wea",
               directoryForConversion="/datadrive/pferrer/SFO_Final_PF/results/tmp")

    print(x.metricASEdetailed())
    print(x.metricASE())
    # with open("ASE.txt", "w") as ASE:
    #     for val in x.metricASEdetailed():
    #         ASE.write("%s\n"%val)

# call the ase calculation
#calc_ASE("results/ASEIll.ill")

# write a function here so that the rows/columns are swapped if necessary



################################################################################################################


####################################################### ALL SDA #################################################
#STEP 1: Perform an annual daylight coefficient simulation. (Diffuse sky simulation only)

import time

def diffuseskycalc():
    #create diffuse sky simulation
    #Create octree
    # print("Create octree at %s"%time.ctime())
    # os.system("oconv scene.rad > octrees/scene.oct")

    #Generate daylight coefficients (-lw should be the reciprocal of -ad)
    # This will take the most time
    #print("CGenerate daylight coefficients (-lw should be the reciprocal of -ad) %s" % time.ctime())
    #os.system("rfluxmtx -I+ -y %s -lw 3.33e-6 -ab 5 -ad 300000 -n 16 - skyglow.rad -i octrees/scene.oct < points.pts > matrices/illum.mtx"%linelength)

    # #Create Annual sky-matrix (diffuse)
    #print("Create Annual sky-matrix (diffuse) %s" % time.ctime())
    os.system("gendaymtx -m 1 -r -28 assets/CA_SAN-FRANCISCO-IAP_724940_TY3.wea > skyvectors/SFOsky.smx")

    # #Matrix Multiplication for diffuse(rmtxop is the command)
    print("Matrix Multiplication for diffuse(rmtxop is the command) %s" % time.ctime())
    os.system("dctimestep matrices/illum.mtx skyvectors/SFOsky.smx > results/Illum.tmp")
    # Compress file so we can load everything incrementally instead of all at once

    # If you're using a small file, just use this:
    #os.system("rmtxop -fa -t -c 47.4 119.9 11.6 results/Illum.tmp > results/illum.ill")

    # however if running a large file that needs compression, run the"comressilluminance function from splitcalc"
    compressIlluminance("results/Illum.tmp", OutputFile= "results/Annual.ill")

    #Create direct sky simulation
    # print("Create direct sky simulation %s" % time.ctime())
    os.system("oconv blackscene.rad > octrees/sceneblack.oct")

    #Generate daylight coefficients (-lw should be the reciprocal of -ad)
    print("Generate daylight coefficients (-lw should be the reciprocal of -ad) %s" % time.ctime())
    os.system("rfluxmtx -I+ -y %s -lw 3.33e-6 -ab 1 -ad 300000 -n 16 - skyglow.rad -i octrees/sceneblack.oct < points.pts > matrices/illum_direct.mtx"%linelength)

    #Create Annual sky-matrix (direct)
    print("Create Annual sky-matrix (direct) %s" % time.ctime())
    os.system("gendaymtx -d -m 1 -r -28 assets/CA_SAN-FRANCISCO-IAP_724940_TY3.wea > skyvectors/SFOsky_direct.smx")

    #Matrix Multiplication for direct (rmtxop is the command)
    print("Matrix Multiplicationfor direct (rmtxop is the command) %s" % time.ctime())
    os.system("dctimestep matrices/illum_direct.mtx skyvectors/SFOsky_direct.smx > results/Illumdir.tmp")

    # if small file, use this:
    # os.system("rmtxop -fa -t -c 47.4 119.9 11.6 results/Illumdir.tmp > results/illumdir.ill")

    # if large file use this:
    compressIlluminance("results/Illumdir.tmp", OutputFile="results/AnnualDir.ill")
    pass

def calc_SDA():
    # This is a class from sarith that converts into daysim, and calculates metrics all at once
    x = Dayill("results/FINAL_Illuminance_Transposed.ill", "points.pts", convertFromRadiance=True,
               weaFile="assets/CA_SAN-FRANCISCO-IAP_724940_TY3.wea", directoryForConversion="results/tmp")
    # print(x.metricSDAdetailed())
    print(x.metricSDA())
    with open("SDA.txt", "w") as SDA:
        for val in x.metricSDAdetailed():
            SDA.write("%s\n"%val)

def combineresults():
    """
    This will take the annual calculation, subtract the less accurate direct portion and add back in the more accurate
    direct portion from the ASE study
    :return:
    """
    os.system("rmtxop results/Annual.ill + -s -1 results/AnnualDir.ill + results/ASEIll.ill > results/FINAL_Illuminance.ill ")
    os.system("rmtxop -t results/FINAL_Illuminance.ill > results/FINAL_Illuminance_Transposed.ill")




# create_suncoef()
#create_sunmatrix()

# Running Calc_ASE is causing an index out of range error.  Get with Sarith about this
# calc_ASE("results/ASEIll.ill")

# diffuseskycalc()
# combineresults()
calc_SDA()

