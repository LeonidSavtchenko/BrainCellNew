TITLE P calcium current (not inactivate)
 
COMMENT
This is adapted for CVODE (by Brown et al 2010) from the original file published in "An Active Membrane Model of the Cerebellar Purkinje Cell 1. Simulation of Current Clamp in Slice".
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX CaP2cvode
        USEION ca READ cai, cao WRITE ica
        RANGE  gcabar, ica, gca
} 
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        gcabar = .0045 (mho/cm2)
        ecacvode = 135 (mV)
	  cai	= 0.40e-4 (mM)		: adjusted for ecacvode=135mV
	  cao	= 2.4	(mM)
	  mon = 1
}
 
STATE {
        m
}
 
ASSIGNED {
        ica (mA/cm2)
        gca minf tau q10 alpha beta sum
}
 
BREAKPOINT {
	  SOLVE state METHOD cnexp
        gca = gcabar * m
        ica = gca* (v-ecacvode)
}
 
UNITSOFF
 
INITIAL {
	m = minf
}

DERIVATIVE state {   :Computes state variables m at the current v.

                :"m" calcium activation system

        
        q10 = 3^((celsius - 37)/10)

        alpha = 8.5/(1+exp((v-8)/(-12.5)))
        beta =  35/(1+exp((v+74)/14.5))
        sum = alpha + beta
        minf = alpha/sum
	  tau = 1/(sum * q10)
	  m' = mon * (minf-m)/tau
}

 
UNITSON


