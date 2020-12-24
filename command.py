import subprocess
from colorama import Fore, Back, Style

def run(command, verbose=False, sync=True):
    command = command.split(' ')
    out = ''
    if (sync):
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=False)
        out = process

    else:
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.wait()
        out, err = process.communicate()
        if (err != ''):
            print(Fore.RED + "REEEEE")
            print(Fore.RED + err)
    # out = str(out, "utf-8")
    if (args.verbose):
        print(out)
    return out
