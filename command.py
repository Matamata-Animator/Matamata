import subprocess
from colorama import Fore, Back, Style

verbose = False


def set_verbose(is_verb):
    global verbose
    verbose = is_verb


def run(command, sync=True):
    command = command.split(' ')
    out = ''
    if sync:
        process = subprocess.run(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True)
        out = process

    else:
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.wait()
        out, err = process.communicate()
        if err != '':
            print(Fore.RED + err)
    # out = str(out, "utf-8")
    if verbose:
        print(out)
    return out
