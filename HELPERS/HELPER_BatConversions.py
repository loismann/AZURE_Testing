
class Convert:
    def __init__(self):
        self.nothing = None

    def bat_to_sh_DGP(self, file_path):
        sh_file = file_path[:-4] + '.sh'
        with open(file_path, 'rb') as infile, open(sh_file, 'wb') as outfile:
            outfile.write('#!/usr/bin/env bash\n\n')
            for i,line in enumerate(infile):
                if i <=4:
                    pass
                else:
                    outfile.write(line + '\n')
            outfile.close()




path = r"C:\Users\pferrer\Desktop\test\21MAR600_IMGInit.bat"
Convert().bat_to_sh_DGP(path)

