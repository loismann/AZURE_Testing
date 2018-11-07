import shutil

# Windows
# Backup_Directory = r"C:\ladybug\AzurePFGlareTesting"
# Main_Directory = r"C:\Users\pferrer\Desktop\test"

#Mac
Main_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles"
Backup_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles Originals"
CopiedHDR_Directory = "/Users/paulferrer/Desktop/TEST"

# Delete all files in Main Directory
shutil.rmtree(Main_Directory)

# Delete all files in the local HDR Directory
# shutil.rmtree(CopiedHDR_Directory)

# Copy over files from Backup Directory
shutil.copytree(Backup_Directory, Main_Directory, symlinks=False, ignore=None)