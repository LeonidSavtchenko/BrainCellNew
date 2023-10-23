TITLE Anomalous rectifier
 
COMMENT
This is adapted for CVODE (by Brown et al 2010) from the original file published in "An Active Membrane Model of the Cerebellar Purkinje Cell 1. Simulation of Current Clamp in Slice".
  
  "Anomalous Rectification in Neurons from Cat Sensorimotor Cortex
    In Vitro" W.J.SPAIN, P.C.SCHWINDT, and W.E.CRILL
           JOURNAL OF NEUROPHYSIOLOGY Vol 57, No.5
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX Khcvode
  	  USEION k WRITE ik
        RANGE  gkbar, gk, ik
} 
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        mon = 1        
	  man = 1
	  nan = 1
        gkbar = .0003 (mho/cm2)
        ekcvode	= -30 (mV)

}
 
STATE {
        m 
}
 
ASSIGNED {
        ik (mA/cm2)
        gk minf mtau ntau q10
}
 
BREAKPOINT {
        SOLVE state METHOD cnexp
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

        minf = 1/(1+exp((v+78)/7))
	  mtau= 38/q10
        ntau = 319/q10
        m' = mon * ( (man * 0.8 * (minf-m)/mtau) + (nan * 0.2 * (minf-m)/ntau) )     
}

 
UNITSON

