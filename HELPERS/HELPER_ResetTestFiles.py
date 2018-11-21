import shutil
import os
import time
import pathlib

# Windows
# Backup_Directory = r"C:\ladybug\AzurePFGlareTesting"n
Backup_Directory = r"C:\ladybug\AzurePFGlareTesting"
Main_Directory = r"C:\Users\pferrer\Desktop\DGP_Cam1"
CopiedHDR_Directory = r"C:\Users\pferrer\Desktop\TEST_CopiedHDRfiles"

#Mac
# Main_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles"
# Backup_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles Originals"
# CopiedHDR_Directory = "/Users/paulferrer/Desktop/TEST"

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def main():
    # Clear out the main director
    if os.path.exists(Main_Directory):
        shutil.rmtree(Main_Directory,False)
        os.mkdir(Main_Directory)
        os.chmod(Main_Directory, 0o777)
    else:
        os.mkdir(Main_Directory)
        os.chmod(Main_Directory, 0o777)

    # Clear out the HDR director
    if os.path.exists(CopiedHDR_Directory):
        shutil.rmtree(CopiedHDR_Directory,False)
        os.mkdir(CopiedHDR_Directory)
        os.chmod(CopiedHDR_Directory, 0o777)
    else:
        os.mkdir(CopiedHDR_Directory)
        os.chmod(CopiedHDR_Directory, 0o777)



    # Copy over files from Backup Directory
    copytree(Backup_Directory, Main_Directory, symlinks=False, ignore=None)
