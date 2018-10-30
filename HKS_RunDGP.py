import os


# TODO: 1. Convert .bat to .sh
class Convert:
    def __init__(self):
        self.nothing = None

    def bat_to_sh_DGP(self, file_path):
        sh_file = file_path[:-4] + '.sh'
        with open(file_path, 'r') as infile, open(sh_file, 'w') as outfile:
            outfile.write('#!/usr/bin/env bash\n\n')
            for i,line in enumerate(infile):
                if i <4:
                    pass
                else:
                    # Go through each string looking for file paths
                    # if you find file paths, replace them with just the file name
                    parse = line.split()
                    replaced = []
                    for segment in parse:
                        if os.path.exists(segment):
                            replaced.append(os.path.basename(segment))
                            print("found a file!")
                        else:
                            replaced.append(segment)
                    new_line = " ".join(replaced)
                    outfile.write(new_line + '\n')
            outfile.close()


# TODO: 2. Create Master Python file to control the Linux Operations
# First make sure that the code works and runs the batch files
# Then figure out how to write all those commands into a new python files
# Testing out creating a python file and running it


# TODO: 3. Copy all files over to linux
# TODO: 4. Run the Master Python file to create and manage jobs



# Run through all files in the current directory, find the batch files,
# Convert them into shell files, then run them

# Get the windows directory we'll need
Main_Directory = input("Paste Folder Location of .bat files for conversion:")

for root, dirs, files in os.walk(os.path.abspath(Main_Directory)):
    for file in files:
        file_path = os.path.join(root, file)
        if file_path.endswith(".bat"):
            Convert().bat_to_sh_DGP(file_path)