TITLE Persistent sodium current
 
COMMENT
This is adapted for CVODE (by Brown et al 2010) from the original file published in "An Active Membrane Model of the Cerebellar Purkinje Cell 1. Simulation of Current Clamp in Slice".
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
 	SUFFIX NaPcvode
	USEION na WRITE ina
	RANGE gnabar, gna
}
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
  	v		(mV)
	celsius	= 37	(degC)
	enacvode	= 45	(mV)
	gnabar	= 0.001 (mho/cm2)
	mon = 1
}
 
STATE {
        m 
}
 
ASSIGNED {
        ina (mA/cm2)
    	  minf
        gna
	  tau q10 alpha beta sum
}
 
BREAKPOINT {
        SOLVE state METHOD cnexp
        gna = gnabar*m*m*m
        ina = gna*(v - enacvode)
  
}
 
UNITSOFF
 
INITIAL {
	
	m = minf
}

 
DERIVATIVE state {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        
        q10 = 3^((celsius - 37)/10)
        
                :"m" sodium activation system

        alpha = 200/(1+exp((v-18)/(-16)))
        beta =  25/(1+exp((v+58)/8))
        sum = alpha + beta
        minf = alpha/sum
	  tau= 1/(q10 * sum)
        m' = mon * (minf-m)/tau      
}
 

 
UNITSON

