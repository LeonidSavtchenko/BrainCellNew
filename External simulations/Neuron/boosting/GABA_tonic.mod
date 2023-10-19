TITLE GABA tonic passive membrane channel
 UNITS {
 	(mV) = (millivolt)
 	(mA) = (milliamp)
 	(S) = (siemens)
 }

 NEURON {
 	SUFFIX GABA_tonic
	NONSPECIFIC_CURRENT i
	RANGE g, e
}

PARAMETER {
	g = 0.000000001	(S/cm2)	<0,1e9>  
	e = -59	(mV)                      
}

ASSIGNED {v (mV)  i (mA/cm2)}
BREAKPOINT {
	i = g*(v - e)}