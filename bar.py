import time
from math import floor


def get_gradient(dec):
    gradient = ' '
    if 1 / 8 <= dec < 2 / 8:
        gradient = '▏'
    elif 2 / 8 <= dec < 3 / 8:
        gradient = '▎'
    elif 3 / 8 <= dec < 4/8:
        gradient = '▍'
    elif 4 / 8 <= dec < 5 / 8:
        gradient = '▌'
    elif 5 / 8 <= dec < 6 / 8:
        gradient = '▋'
    elif 6 / 8 <= dec < 7 / 8:
        gradient = '▊'
    elif 7 / 8 <= dec < 8 / 8:
        gradient = '▉'

    return gradient


def print_bar(numerator, denominator, prefix='', length=100, char='█'):
    pre = f'\r{prefix} |'
    bar = int((numerator / denominator) * length) * char
    dec = ((numerator / denominator) * length) - floor(int((numerator / denominator) * length))
    gradient = get_gradient(dec)
    space = (length - len(bar) - 1) * ' '
    percentage = int((numerator / denominator) * 100)
    print(f'{pre}{bar}{gradient}{space}| {percentage}% [{numerator}/{denominator}]', end='')


if __name__ == '__main__':
    denom = 1000
    for i in range(denom):
        print_bar(i, denom)
        time.sleep(0.05)
    print_bar(denom, denom)
