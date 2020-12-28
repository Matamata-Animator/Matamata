import subprocess
import os
import sys
from colorama import Fore, Back, Style

verbose = False


def set_verbose(is_verb):
    global verbose
    verbose = is_verb


def run(command, sync=True):
    command = command.split(' ')
    out = ''
    if not verbose:
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = process.communicate()
    if sync:
        p_status = process.wait()
    if not verbose:
        sys.stdout = old_stdout
    return out
