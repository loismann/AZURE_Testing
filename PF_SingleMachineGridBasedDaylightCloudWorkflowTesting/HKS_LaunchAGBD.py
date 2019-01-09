import subprocess
import os
import time
from collections import defaultdict
import shutil
import zipfile

##### Functions

if __name__ == "__main__":
    print("HKS_LaunchAGBD.py copied over and launched successfully")
    # Get the main directory we're working in
    Main_Directory = "/home/pferrer/new"
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


