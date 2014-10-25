<<<<<<< HEAD
#!/usr/bin/python

=======
>>>>>>> dev
import curses
from pymlab import config
import sys

<<<<<<< HEAD
port = 0
=======
port = eval(sys.argv[1])
>>>>>>> dev

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

<<<<<<< HEAD
freq = 10000000
FREQ_X = 10
FREQ_Y = 2

e = 2
f = FREQ_X - 1
=======
freq = 12345678
FREQ_X = 10
FREQ_Y = 2

e=2
f=FREQ_X-1
>>>>>>> dev

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)

def show_freq():
    freq_str = str(freq)
    stdscr.addstr(FREQ_Y, FREQ_X - len(freq_str), freq_str)

<<<<<<< HEAD
while 1:
    try:
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
=======
def show_freqa():
    vis_str = str(freq)[:2]+' '+str(freq)[2:5]+' '+str(freq)[5:9]
    stdscr.addstr(FREQ_Y, FREQ_X - len(vis_str), vis_str)


t=(2, 6)

while 1:
    try:
        show_freqa()
        stdscr.move(e, f)
        c = stdscr.getch()
        if c == curses.KEY_RIGHT:
            f = f + 1 
        elif c == curses.KEY_LEFT:
            f = f - 1
        elif c == curses.KEY_UP:
            if f in t:
                pass
            if f in [0, 1]:
                freq = freq + 10 ** (7 - f)
                show_freqa()
            if f in [3, 4, 5]:
                freq = freq + 10 ** (8 - f)
                show_freqa()
            if f in [7, 8, 9]:
                freq = freq + 10 ** (9 - f)
                show_freqa()
            
            #si570_set_freq(freq)
        elif c == curses.KEY_DOWN:
            if f in t:
                pass
            if f in [0, 1]:
                freq = freq - 10 ** (7 - f)
                show_freqa()
            if f in [3, 4, 5]:
                freq = freq - 10 ** (8 - f)
                show_freqa()
            if f in [7, 8, 9]:
                freq = freq - 10 ** (9 - f)
                show_freqa()        
            #freq = freq - 10 ** (9 - f)
            #si570_set_freq(freq)
>>>>>>> dev
    except KeyboardInterrupt:
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        sys.exit()

<<<<<<< HEAD
curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()
=======

curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()
>>>>>>> dev
