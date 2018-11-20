import shutil
import os

# Windows
# Backup_Directory = r"C:\ladybug\AzurePFGlareTesting"n
Backup_Directory = r"C:\ladybug\AzurePFGlareTesting"
Main_Directory = r"C:\Users\pferrer\Desktop\DGP_Cam1"
CopiedHDR_Directory = r"C:\Users\pferrer\Desktop\TEST_CopiedHDRfiles"

#Mac
# Main_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles"
# Backup_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles Originals"
# CopiedHDR_Directory = "/Users/paulferrer/Desktop/TEST"


def main():
    # Delete all files in Main Directory
    if os.path.exists(Main_Directory):
        pass
        # shutil.rmtree(Main_Directory)
    else:
        os.mkdir(Main_Directory)



    # Delete all files in the local HDR Directory
    if os.path.exists(CopiedHDR_Directory):
        pass
        # shutil.rmtree(CopiedHDR_Directory)
    else:
        os.mkdir(CopiedHDR_Directory)

    # Copy over files from Backup Directory

    # shutil.copytree(Backup_Directory, Main_Directory, symlinks=False, ignore=None)