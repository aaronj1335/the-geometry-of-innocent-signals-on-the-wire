#!/usr/bin/env python
"""
a test shell for the 'sig' module.  it's handy to open a python shell and run
this during testing:

    execfile('sig/test.py')

"""

if 'plot' not in globals():
    from pylab import *


execfile('sig/__init__.py')

s = Signal(raw_signal=raw_signal('out.pcm'))
d = Decoder(signal=s, filtering='medfilt')

def vline(x, color='r'):
    vlines(x, -100000, 100000, color)

def incremental(s=s, d=d):
    vline(s.start_time, 'g')
    vline(s.end_time, 'g')
    plot(s.x, s.smoothed(10))
    for i in d.bits():
        vline(i[1] / s.FS)
    show()

def bits(d=d):
    return ''.join(str(b[0]) for b in d.bits())

def num(bits=bits()):
    cc = ''.join(n for n in cc_num(bits))
    if len(cc) < 16:
        cc = ''.join(n for n in cc_num(reversed(bits)))
    return cc
