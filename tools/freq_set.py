import curses
from pymlab import config
import sys

port = eval(sys.argv[1])

cfg = config.Config(i2c = {"port": port}, bus = [
                    {"type": "i2chub", "address": 0x70,
                     "children": [{"name":"clkgen", "type":"clkgen01", "channel": 1}]}])
cfg.initialize()
fgen = cfg.get_device("clkgen")
fgen.route()
fgen.recall_nvm()
si570_freq = 10.0

def si570_set_freq(freq):
    global si570_freq
    freq_mhz = float(freq) / 1e6
    fgen.set_freq(si570_freq, freq_mhz)
    si570_freq = freq_mhz

freq = 10000000
FREQ_X = 10
FREQ_Y = 2

e=2
f=FREQ_X-1

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)

def show_freq():
    freq_str = str(freq)
    stdscr.addstr(FREQ_Y, FREQ_X - len(freq_str), freq_str)

while 1:
    show_freq()
    stdscr.move(e, f)
    c = stdscr.getch()
    if c == curses.KEY_RIGHT:
        f = f + 1     
    elif c == curses.KEY_LEFT:
        f = f - 1
    elif c == curses.KEY_UP:
        freq = freq + 10 ** (9 - f)
        show_freq()
        si570_set_freq(freq)
    elif c == curses.KEY_DOWN:
        freq = freq - 10 ** (9 - f)
        show_freq()
        si570_set_freq(freq)
    elif c == ord("q"):
        break


curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()