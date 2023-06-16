
from math import *

def myDistFunc(x):
    y = x/10 + 50*sin(2*pi*x/200) * tanh(x/100)
    return y
    