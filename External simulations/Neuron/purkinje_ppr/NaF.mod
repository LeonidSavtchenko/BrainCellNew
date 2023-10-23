TITLE Fast sodium current
 
COMMENT
  from "An Active Membrane Model of the Cerebellar Purkinje Cell
        1. Simulation of Current Clamp in Slice"
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX NaF
	USEION na WRITE ina
        RANGE  gnabar, gna, minf, hinf, mexp, hexp
} 
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        dt (ms)
        gnabar	= 7.5 (mho/cm2)
        ena	= 45 (mV)
	mon = 1
	hon = 1
}
 
STATE {
        m h
}
 
ASSIGNED {
        ina (mA/cm2)
        gna minf hinf mexp hexp 
}
 
BREAKPOINT {
        SOLVE states
        gna = gnabar *m*m* m*h 
	ina = gna* (v-ena)
}
 
UNITSOFF
 
INITIAL {
	rates(v)
	m = minf
	h = hinf
}

PROCEDURE states() {  :Computes state variables m, h
        rates(v)      :             at the current v and dt.
        m = mon * (m + mexp*(minf-m))
        h = hon * (h + hexp*(hinf-h))
}
 
PROCEDURE rates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        LOCAL  q10, tinc, alpha, beta, sum
        TABLE minf, mexp, hinf, hexp DEPEND dt, celsius FROM -400 TO 300 WITH 700
        q10 = 3^((celsius - 37)/10)
        tinc = -dt * q10
                :"m" sodium activation system
        alpha = 35/exp((v+5)/(-10))
        beta =  7/exp((v+65)/20)
        sum = alpha + beta
        minf = alpha/sum
        mexp = 1 - exp(tinc*sum)
                :"h" sodium inactivation system
        alpha = 0.225/(1+exp((v+80)/10))
        beta = 7.5/exp((v-3)/(-18))
        sum = alpha + beta
        hinf = alpha/sum
        hexp = 1 - exp(tinc*sum)
}

 
UNITSON

