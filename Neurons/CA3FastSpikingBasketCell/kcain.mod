TITLE Slow Ca-dependent potassium current
:
:   Ca++ dependent K+ current responsible for slow AHP

NEURON {
	SUFFIX kcain
	USEION k READ ko, ki WRITE ik
	USEION ca READ cai
	RANGE  gbar, po, ik
	GLOBAL m_inf, tau_m
}


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(molar) = (1/liter)
	(mM) = (millimolar)
}

ASSIGNED {       : parameters needed to solve DE
	v               (mV)
	celsius         (degC)
	ek              (mV)
	cai             (mM)           : initial [Ca]i
	ik              (mA/cm2)
	po
	ki 		(mM)
	ko		(mM)
	m_inf
	tau_m           (ms)
:	h_inf				:inactivation 
:	tau_h		(ms)
:	taumin
}

PARAMETER {
	gbar    = 10   (mho/cm2)
:        ek	 	(mV)
	taumin  = 0	(ms)  :(150)
	b 	= 0.008 (/ms)  : changed oct 17, 2006 for pfc (0.3)
	:b 	= 0.8		: value for CA1 neuron(2006)
:	tau_h	= 300	(ms)
}


STATE {
	m   
}

BREAKPOINT { 
	SOLVE states METHOD cnexp
	ek = 25 * log(ko/ki)
	po = m*m
	ik = gbar*po*(v - ek)    : potassium current induced by this channel
}

DERIVATIVE states {
	rates(cai)
:	m'=(-1/(tau_m))*(m-(m_inf)) 

	m' = (m_inf - m) / tau_m : old equation
:	h'=(h_inf - h)/tau_h	
	
} 


INITIAL {
	rates(cai)
	m = 0
:	m = m_inf

:	h = h_inf
}


PROCEDURE rates(cai(mM)) { 
	LOCAL a
:	a=100
:	m_inf=(a*cai*cai)/(a*cai*cai+b)
:	tau_m=(1/(a*cai*cai+b))
	
:old equations	
	a = cai/b
	m_inf = a/(a+1)
:	tau_m=600
	tau_m = taumin+ 1(ms)*1(mM)*b/(cai+b)

:inactivation
:	h_inf= ah/(ah+1)
}
