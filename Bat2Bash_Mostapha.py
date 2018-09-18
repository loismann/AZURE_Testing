def bat_to_sh(file_path):
    """Convert a honeybee .bat file to .sh file.

    WARNING: This is a very simple function and doesn't handle any edge cases.
    """
    sh_file = file_path[:-4] + '.sh'
    with open(file_path, 'rb') as inf, open(sh_file, 'wb') as outf:
        outf.write('#!/usr/bin/env bash\n\n')
        for line in inf:
            # pass the path lines, etc to get to the commands
            if line.strip():
                continue
            else:
                break

        for line in inf:
            if line.startswith('echo'):
                continue
            # replace c:\radiance\bin and also chanege \\ to /
            modified_line = line.replace('c:\\radiance\\bin\\', '').replace('\\', '/')
            outf.write(modified_line)

    print('bash file is created at:\n\t%s' % sh_file)
    return sh_file


if __name__ == '__main__':
    file_path = \
        r'C:\ladybug\170914_DA_Study_with_DC\gridbased_daylightcoeff\commands.bat'
    bash_file_path = bat_to_sh(file_path)