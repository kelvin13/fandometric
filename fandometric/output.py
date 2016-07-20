from itertools import chain

graybg  = '\033[48;5;235m'
blackbg = '\033[48;5;0m'
white   = '\033[38;5;15m'

fail    = '\033[38;5;197m'
bold    = '\033[1m'
warning = '\033[38;5;220m' + bold
endc    = '\033[0m'
succ    = '\033[38;5;86m'
invert  = '\033[7m'

def mono_align(width, align, color, text):
    if align:
        if align == 1:
            return color, ('{:>' + str(width) + '}').format(text), endc
        else:
            return color, ('{:<' + str(width) + '}').format(text), endc
    else:
        return color, ('{:^' + str(width) + '}').format(text), endc
def render_table( * tables ):
    cfi = chain.from_iterable
    return '\n'.join(cfi((''.join(cfi(mono_align( * cell ) for cell in row)) for row in table) for table in tables))
