TITLE Persistent potassium current
 
COMMENT
  from "An Active Membrane Model of the Cerebellar Purkinje Cell
        1. Simulation of Current Clamp in Slice"
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX KM
	USEION k  WRITE ik
        RANGE  gkbar, gk, minf,  mexp
} 
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        dt (ms)
        gkbar	= .00004 (mho/cm2)
        ek	= -85 (mV)
	mon = 1
}
 
STATE {
        m 
}
 
ASSIGNED {
        ik (mA/cm2)
        gk minf  mexp 
}
 
BREAKPOINT {
        SOLVE states
        gk = gkbar *m
	ik = gk* (v-ek)
}
 
UNITSOFF
 
INITIAL {
	rates(v)
	m = minf
	
}

PROCEDURE states() {  :Computes state variables m
        rates(v)      :             at the current v and dt.
        m = mon * (m + mexp*(minf-m))
}
 
PROCEDURE rates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        LOCAL  q10, tinc, sum
        TABLE minf, mexp DEPEND dt, celsius FROM -400 TO 300 WITH 700
        q10 = 3^((celsius - 37)/10)
        tinc = -dt * q10
                :"m" potassium activation system
        sum = 3.3*(exp((v+35)/40)+exp(-(v+35)/20))/200
        minf = 1.0 / (1+exp(-(v+35)/10))
        mexp = 1 - exp(tinc*sum)
               
}

 
UNITSON

