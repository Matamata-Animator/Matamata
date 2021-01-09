import subprocess
import os
import sys
from colorama import Fore, Back, Style

verbose = False
old_stdout = sys.stdout


def set_verbose(is_verb):
    global verbose
    verbose = is_verb


def run(command, sync=True):
    command = command.split(' ')
    out = ''
    if not verbose:
        sys.stdout = open(os.devnull, 'w')
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if sync:
        (out, err) = process.communicate()
        p_status = process.wait()
    if not verbose:
        sys.stdout = old_stdout
    if type(out) is bytes:
        out = out.decode('utf-8')
    return out
