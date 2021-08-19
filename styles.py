class C:
    # Foreground:
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

class BC:
    # Background:
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47

class SC:
    RESET = 0
    BOLD = 1


def mv_cursor(x=0, y=0, text=''):
    return f'\033[{y+1};{x+1}H{text}'

def cls():
    return '\033[2J'

def color_fg(c):
    return f'\033[38;5;{c}m'

def color_bg(c):
    return f'\033[48;5;{c}m'

def color(c):
    return f'\033[{c}m'
