import subprocess
import os
import time
from collections import defaultdict
import shutil
import zipfile

##### Functions

if __name__ == "__main__":
    print("HKS_LaunchPITGBD.py copied over and launched successfully")
    # Get the main directory we're working in
    Main_Directory = "/home/pferrer/new"
    # set the Main_Directory to be the current working directory
    os.chdir(Main_Directory)
    # Make the directory fully R/W
    # os.chmod(Main_Directory,777)

    # Unzip the working files
    destination_file_path = None
    for root, dir, files in os.walk(Main_Directory):
        for file in files:
            if str(file).endswith('.zip'):
                print('found a zip file')
                destination_file_path = os.path.join(Main_Directory, file)
        # Unzip the working files to the Main Directory
    with zipfile.ZipFile(destination_file_path, 'r') as zip_ref:
        zip_ref.extractall(Main_Directory)

    # remove the zip file
    os.remove(destination_file_path)
    print("launched 'HKS_LaunchDGP' file remotely and unzipped files")

    # run the radiance calculations
    # this is copied in right now but will be parametric in the future
    # loop through all the files in the main directory and identify each one for use in the radiance calcs

    SkyFile = None
    PointsFile = None
    MaterialFile = None
    GeometryFile = None

    SimFileList = []
    for file in os.listdir(Main_Directory):

        if "material" in file:
            MaterialFile = file
            SimFileList.append(MaterialFile)
        elif file.endswith(".rad") and "material" not in file:
            GeometryFile = file
            SimFileList.append(GeometryFile)
        elif file.endswith(".sky"):
            SkyFile = file
            SimFileList.append(SkyFile)
        elif file.endswith(".pts"):
            PointsFile = file

    print(SimFileList)
    print("Current working directory is" + os.getcwd())

    # Create the octree
    os.system("oconv -r 2048 -f {0} {1} {2} > OCTFILE.oct".format(MaterialFile,SkyFile,GeometryFile))

    # Run the simulation at LOW settings
    os.system("rtrace -I -h -dp 64 -ds 0.5 -dt 0.5 -dc 0.25 -dr 0 -st 0.85 -lr 4 -lw 0.05 -ab 2 -ad 1000 -as 128 -ar 300 -aa 0.1  -af AMBFILE.amb -e error.log OCTFILE.oct < {0} > RESULTSFILE.res".format(PointsFile))

    # # Run the simulation at MEDIUM settings
    # os.system("rtrace -I -h -dp 256 -ds 0.25 -dt 0.25 -dc 0.5 -dr 1 -st 0.5 -lr 6 -lw 0.01 -ab 3 -ad 2048 -as 2048 -ar 300 -aa 0.1  -af AMBFILE.amb -e error.log OCTFILE.oct < {0} > RESULTSFILE.res".format(PointsFile))



