def print_bar(numerator, denominator, prefix='', length=100, char='█'):
    pre = f'\r{prefix} |'
    bar = int((numerator / denominator) * length) * char
    space = (length - len(bar)) * ' '
    percentage = int((numerator/denominator)*100)
    print(f'{pre}{bar}{space}| {percentage}% [{numerator}/{denominator}]', end='')
