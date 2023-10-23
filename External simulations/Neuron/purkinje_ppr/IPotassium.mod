TITLE passive membrane channel with Glu conductance

UNITS {
	(mV) = (millivolt)
	(mA) = (milliamp)
	(S) = (siemens)
	(molar) = (1/liter)
    (mM) =	(millimolar)
}

NEURON {
	SUFFIX IKa
	USEION k READ ki, ko WRITE ik	
	:NONSPECIFIC_CURRENT i
    RANGE gk
}

PARAMETER {
	gk = .1	(S/cm2)	<0,1e9>
	:ki = 120 (mM)   <0,1e9>
	
}

ASSIGNED {

v (mV)  
ik (mA/cm2)
ki      (mM)
ko      (mM)

}

BREAKPOINT {
	ik = gk*(v - 25 (mV)*log(ko/ki))
}
