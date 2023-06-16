COMMENT
Longitudinal diffusion of potassium (no buffering)
Savtchenko et al., 2018
ENDCOMMENT

NEURON {
	SUFFIX kdifl
	USEION k READ ik, ki WRITE ki
	RANGE Dk, ki0, iextra
}

UNITS {
	
	(mM) = (milli/liter)
	(um) = (micron)
	FARADAY = (faraday) (coulomb)
	PI = (pi) (1)
	
}

INITIAL {
	
	ki = ki0
	
	ka = ki
}
PARAMETER {
    ki0 = 110 (mM)
	Dk = 0.6 (micron2/ms)
	iextra = 0 (milliamp/cm2)
	
}

ASSIGNED {
	ik (milliamp/cm2)
	
	diam (um)
	ki       (mM)
}

STATE {
	ka (mM)
}

BREAKPOINT {
	SOLVE conc METHOD sparse
}

KINETIC conc {
	COMPARTMENT PI*diam*diam/4 {ka}
	LONGITUDINAL_DIFFUSION Dk*diam*diam {ka}
	: LONGITUDINAL_DIFFUSION Dk {ka}
	~ ka << (-(ik-iextra)/(FARADAY)*PI*diam*(1e4))
	ki = ka
}