TITLE A current
 
COMMENT
This is adapted for CVODE (by Brown et al 2010) from the original file published in "An Active Membrane Model of the Cerebellar Purkinje Cell 1. Simulation of Current Clamp in Slice".
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX KAcvode
	  USEION k WRITE ik
        RANGE  gkbar, gk, ik
} 
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        mon = 1
	  hon = 1
        gkbar	= .015 (mho/cm2)
        ekcvode	= -85 (mV)

}
 
STATE {
        m h
}
 
ASSIGNED {
        ik (mA/cm2)
        gk minf hinf tau q10 alpha beta sum 
}
 
BREAKPOINT {
        SOLVE state METHOD cnexp
        gk = gkbar *m*m*m* m*h 
	ik = gk* (v-ekcvode)
}
 
UNITSOFF
 
INITIAL {
	
	m = minf
	h = hinf
}


DERIVATIVE state {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        
            q10 = 3^((celsius - 37)/10)
        
                :"m" potassium activation system
        alpha = 1.4/(1+exp((v+27)/(-12)))
        beta =  0.49/(1+exp((v+30)/4))
        sum = alpha + beta
        minf = alpha/sum
	  tau = 1/(q10 * sum)
        m' = mon * (minf-m)/tau      

                :"h" potassium inactivation system

        alpha = 0.0175/(1+exp((v+50)/8))
        beta = 1.3/(1+exp((v+13)/(-10)))
        sum = alpha + beta
        hinf = alpha/sum
	  tau = 1/(q10 * sum)
    	  h' = hon * (hinf-h)/tau
}

 
UNITSON

