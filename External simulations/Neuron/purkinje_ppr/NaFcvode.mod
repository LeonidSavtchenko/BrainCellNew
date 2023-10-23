TITLE Fast sodium current
 
COMMENT
This is adapted for CVODE (by Brown et al 2010) from the original file published in "An Active Membrane Model of the Cerebellar Purkinje Cell 1. Simulation of Current Clamp in Slice".
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX NaFcvode
	USEION na WRITE ina
        RANGE  gnabar, gna
} 
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        
        gnabar	= 7.5 (mho/cm2)
        enacvode	= 45 (mV)
	mon = 1
	hon = 1
}
 
STATE {
        m h
}
 
ASSIGNED {
        ina (mA/cm2)
        gna minf hinf tau q10 alpha beta sum
}
 
BREAKPOINT {
        SOLVE state METHOD cnexp
        gna = gnabar *m*m* m*h 
	ina = gna* (v-enacvode)
}
 
UNITSOFF
 
INITIAL {
	
	m = minf
	h = hinf
}


DERIVATIVE state {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        
        q10 = 3^((celsius - 37)/10)
        
                :"m" sodium activation system

        alpha = 35/exp((v+5)/(-10))
        beta =  7/exp((v+65)/20)
        sum = alpha + beta
        minf = alpha/sum
	  tau= 1/(q10 * sum)
        m' = mon * (minf-m)/tau      

                :"h" sodium inactivation system

        alpha = 0.225/(1+exp((v+80)/10))
        beta = 7.5/exp((v-3)/(-18))
        sum = alpha + beta
        hinf = alpha/sum
    	  tau = 1/(q10 * sum)
        h' = hon * (hinf-h)/tau      
}

 
UNITSON

