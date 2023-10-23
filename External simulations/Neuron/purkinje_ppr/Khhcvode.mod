TITLE gsquid.mod   squid potassium channel
 
COMMENT

This is adapted for CVODE (by Brown et al 2010) from the original
Hodgkin-Huxley treatment for the set of sodium, potassium, and leakage
channels found in the squid giant axon membrane.("A quantitative
description of membrane current and its application conduction and
excitation in nerve" J.Physiol. (Lond.) 117:500-544 (1952).) Membrane
voltage is in absolute mV and has been reversed in polarity from the
original HH convention and shifted to reflect a resting potential of
close to -65 mV. (This text was written by SW Jaslove 6 March, 1992,
with exception of the clause "adapted for CVODE(by Brown et al
2010)".)

ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX Khhcvode
        USEION k WRITE ik
        RANGE   gk,  gkbar, ik
        
}
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)      
        gkbar = .036 (mho/cm2)
        ekcvode = -85(mV)
        non =1
}
 
STATE {
         n
}
 
ASSIGNED {
        ik (mA/cm2)
        gk ninf tau q10 alpha beta sum 
}
 
BREAKPOINT {
        SOLVE state METHOD cnexp : see http://www.neuron.yale.edu/phpBB/viewtopic.php?f=28&t=592
        gk  = gkbar*n*n*n*n

        ik = gk*(v - ekcvode)      
}
 
UNITSOFF
 
INITIAL {
	
	n = ninf
}

DERIVATIVE state {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        

        q10 = 3^((celsius - 37)/10)
        
                :"n" potassium activation system
        alpha = .01*vtrapcvode(-(v+55),10) 
        beta = .125*exp(-(v+65)/80)
        sum = alpha + beta
        ninf = alpha/sum
        tau= 1/(q10 * sum)
        n' = non * (ninf-n)/tau      
}

FUNCTION vtrapcvode(x,y) {  :Traps for 0 in denominator of rate eqns.
        if (fabs(x/y) < 1e-6) {
                vtrapcvode = y*(1 - x/y/2)
        }else{	
                vtrapcvode = x/(exp(x/y) - 1)
        }
}
 
UNITSON


