TITLE Persistent potassium current
 
COMMENT
This is adapted for CVODE (by Brown et al 2010) from the original file published in "An Active Membrane Model of the Cerebellar Purkinje Cell 1. Simulation of Current Clamp in Slice".
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX KMcvode
	  USEION k  WRITE ik
        RANGE  gkbar, gk, minf
} 
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        mon = 1
        gkbar	= .00004 (mho/cm2)
        ekcvode	= -85 (mV)

}
 
STATE {
        m 
}
 
ASSIGNED {
        ik (mA/cm2)
        gk minf tau q10 alpha beta sum 
}
 
BREAKPOINT {
        SOLVE state METHOD cnexp : see http://www.neuron.yale.edu/phpBB/viewtopic.php?f=28&t=592
        gk = gkbar *m
    	  ik = gk* (v-ekcvode)
}
 
UNITSOFF
 
INITIAL {
	
	m = minf
}


DERIVATIVE state {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.

        q10 = 3^((celsius - 37)/10)
        
                :"m" potassium activation system

        sum = 3.3*(exp((v+35)/40)+exp(-(v+35)/20))/200
        minf = 1.0 / (1+exp(-(v+35)/10))
	  tau= 1/(q10 * sum)
        m' = mon * (minf-m)/tau      
              
}

 
UNITSON

