import subprocess
from colorama import Fore, Back, Style

verbose = False


def set_verbose(is_verb):
    global verbose
    verbose = is_verb


def run(command, sync=True):
    command = command.split(' ')
    out = ''
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (out, err) = process.communicate()
    if sync:
        p_status = process.wait()
    if verbose:
        print(out)
    return out
