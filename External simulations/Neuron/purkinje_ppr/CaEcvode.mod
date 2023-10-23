TITLE E calcium current
 
COMMENT
This is adapted for CVODE (by Brown et al 2010) from the original file published in "An Active Membrane Model of the Cerebellar Purkinje Cell 1. Simulation of Current Clamp in Slice".
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX CaEcvode
        USEION ca READ cai, cao WRITE ica
        RANGE  gcabar, ica, gca
} 
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        mon = 1
	  hon = 1
        gcabar = .0005 (mho/cm2)
        ecacvode = 135 (mV)
   	  cai	= 0.40e-4 (mM)		: adjusted for ecacvode=135mV
	  cao	= 2.4	(mM)

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

        alpha = 2.6/(1+exp((v+7)/(-8)))
        beta =  0.18/(1+exp((v+26)/4))
        sum = alpha + beta
        minf = alpha/sum
	  tau= 4/(q10 *sum)
        m' = mon * (minf-m)/tau      

                :"h" calcium inactivation system

        alpha = 0.0025/(1+exp((v+32)/8))
        beta = 0.19/(1+exp((v+42)/(-10)))
        sum = alpha + beta
        hinf = alpha/sum
	  tau = 10/(q10 * sum)
	  h' = hon * (hinf-h)/tau
}

 
UNITSON

