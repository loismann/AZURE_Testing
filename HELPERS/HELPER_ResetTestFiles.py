import shutil
import os
import time
import pathlib
from HELPERS.HELPER_Login_Info import Login

login = Login()
Backup_Directory = login.Backup_Directory
Main_Directory = login.Local_Main_Directory
CopiedHDR_Directory = login.Local_HDR_Directory

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
