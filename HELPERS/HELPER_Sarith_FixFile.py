import os

def sarith_fix():
    for fname in os.listdir(os.getcwd()):
        dir = (os.getcwd())
        if ".sh" in fname and "new" not in fname:
            name,ext = os.path.splitext(fname)
            newname = name + "new." + ext
            with open(fname) as f, open(newname, "w") as f2:
                for lines in f:
                    if lines.strip():
                        f2.write(lines.strip() + '\n')
                    print(list(lines))
            os.rename(newname,fname)
