import time
from math import floor
import shutil


def get_gradient(dec):
    gradient = ' '
    if 1 / 8 <= dec < 5 / 8:
        gradient = '▌'
    elif 5 / 8 <= dec <= 8 / 8:
        gradient = '█'

    return gradient


def print_bar(numerator, denominator, prefix='', length=shutil.get_terminal_size((80, 20))[0], char='█'):
    numerator = min(numerator, denominator)
    pre = f'{prefix} |'
    length -= 2 * len(str(denominator)) + 15 + len(pre)
    bar = int((numerator / denominator) * length) * char
    dec = ((numerator / denominator) * length) - floor(int((numerator / denominator) * length))
    gradient = get_gradient(dec)
    space = (length - len(bar) - 1) * ' '
    percentage = int((numerator / denominator) * 100)
    print(f'\r{pre}{bar}{gradient}{space}| {percentage}% [{numerator}/{denominator}]', end='')


if __name__ == '__main__':
    denom = 1000
    for i in range(denom):
        print_bar(i, denom)
        time.sleep(0.05)
    print_bar(denom, denom)
