import shutil

# Windows
Main_Directory = r"C:\Users\pferrer\Desktop\test"
Backup_Directory = r"C:\ladybug\AzurePFGlareTesting"

#Mac
# Main_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles"
# Backup_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles Originals"

# Delete all files in Main Directory
shutil.rmtree(Main_Directory)
# Copy over files from Backup Directory
shutil.copytree(Backup_Directory, Main_Directory, symlinks=False, ignore=None)