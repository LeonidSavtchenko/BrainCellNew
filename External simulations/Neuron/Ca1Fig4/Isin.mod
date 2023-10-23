:NMODL for Sinusoid IClamp: 
:Sinusoid current clamp 
: The code was download from https://www.neuron.yale.edu/phpBB/viewtopic.php?t=1250

NEURON {
    POINT_PROCESS IClampSin
    RANGE del, dur, amp, freq, phase, bias 
    ELECTRODE_CURRENT i
} 

UNITS {
    (nA) = (nanoamp)
}

PARAMETER {
    del=100000 (ms) 
    dur=0 (ms) 
    amp=0 (nA) 
    freq=1 (Hz) 
    phase=0 (rad) 
    bias=0 (nA) 
    PI=3.14159265358979323846
}

ASSIGNED {
    i (nA)
}

BREAKPOINT {
    at_time(del) 
    at_time(del+dur)

    if (t < del+dur && t>del) { 
        i = amp*sin(2*PI*freq*(t-del)/1000+phase)+bias 
    } else {
        i = 0
    }
}