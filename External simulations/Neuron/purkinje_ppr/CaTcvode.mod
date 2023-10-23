TITLE T calcium current
 
COMMENT
This is adapted for CVODE (by Brown et al 2010) from the original file published in "An Active Membrane Model of the Cerebellar Purkinje Cell 1. Simulation of Current Clamp in Slice".
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX CaTcvode
        USEION ca READ cai, cao WRITE ica
        RANGE  gcabar, ica, gca
} 
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        
        gcabar = .0005 (mho/cm2)
        ecacvode = 135 (mV)
   	  cai	= 0.40e-4 (mM)		: adjusted for ecacvode=135mV
	  cao	= 2.4	(mM)
	  mon = 1
	  hon = 1
	  alphaexp = 1
	  betaexp = 1
}
 
STATE {
        m h
}
 
ASSIGNED {
        ica (mA/cm2)
        gca minf tau q10 alpha beta sum hinf
}
 
BREAKPOINT {
        SOLVE state METHOD cnexp
        gca = gcabar * m*h
	ica = gca* (v-ecacvode)
}
 
UNITSOFF
 
INITIAL {
	
	m = minf
	h = hinf
}

 
DERIVATIVE state {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        
        q10 = 3^((celsius - 37)/10)
        
                :"m" calcium activation system

        alpha = 2.6/(1+exp((v+21)/(-8)))
        beta =  0.18/(1+exp((v+40)/4))
        sum = alpha + beta
        minf = alpha/sum
	  tau= 1/(q10 * sum)
        m' = mon * (minf-m)/tau      

                :"h" calcium inactivation system

        alpha = 0.0025/(1+ (alphaexp * exp((v+40)/8)))
        beta = 0.19/(1+ (betaexp * exp((v+50)/(-10))))
        sum = alpha + beta
        hinf = alpha/sum
	  tau = 1/(q10 * sum)
	  h' = hon * (hinf-h)/tau
}

 
UNITSON

