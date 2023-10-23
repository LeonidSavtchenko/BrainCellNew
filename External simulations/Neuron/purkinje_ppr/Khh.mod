TITLE gsquid.mod   squid potassium channel
 
COMMENT
This is the original Hodgkin-Huxley treatment for the set of sodium, potassium, and leakage channels found in the squid giant axon membrane.("A quantitative description of membrane current and its application 
conduction and excitation in nerve" J.Physiol. (Lond.) 117:500-544 (1952).)
Membrane voltage is in absolute mV and has been reversed in polarity
from the original HH convention and shifted to reflect a resting potential
of close to -65 mV. (This text was written by SW Jaslove  6 March, 1992.)
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX Khh
        USEION k WRITE ik
        RANGE   gk,  gkbar, ik
        GLOBAL  ninf, nexp
}
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        dt (ms)
        gkbar = .036 (mho/cm2)
        ek = -85(mV)
	non = 1
}
 
STATE {
         n
}
 
ASSIGNED {
        ik (mA/cm2)
        gk ninf nexp
}
 
BREAKPOINT {
        SOLVE states
        gk  = gkbar*n*n*n*n

        ik = gk*(v - ek)      
}
 
UNITSOFF
 
INITIAL {
	rates(v)
	n = ninf
}

PROCEDURE states() {  :Computes state variable n 
        rates(v)      :             at the current v and dt.
        n = non * (n + nexp*(ninf-n))
}
 
PROCEDURE rates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        LOCAL  q10, tinc, alpha, beta, sum
        TABLE ninf, nexp DEPEND dt, celsius FROM -400 TO 300 WITH 700
        q10 = 3^((celsius - 37)/10)
        tinc = -dt * q10
                :"n" potassium activation system
        alpha = .01*vtrap(-(v+55),10) 
        beta = .125*exp(-(v+65)/80)
        sum = alpha + beta
        ninf = alpha/sum
        nexp = 1 - exp(tinc*sum)
}

FUNCTION vtrap(x,y) {  :Traps for 0 in denominator of rate eqns.
        if (fabs(x/y) < 1e-6) {
                vtrap = y*(1 - x/y/2)
        }else{
                vtrap = x/(exp(x/y) - 1)
        }
}
 
UNITSON

