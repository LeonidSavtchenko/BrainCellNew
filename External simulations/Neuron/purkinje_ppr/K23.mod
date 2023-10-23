TITLE K2 calcium-activated potassium current
: Calcium activated K channel.

COMMENT
  from "An Active Membrane Model of the Cerebellar Purkinje Cell
        1. Simulation of Current Clamp in Slice"
ENDCOMMENT

UNITS {
	(molar) = (1/liter)
}

UNITS {
	(mV) =	(millivolt)
	(mA) =	(milliamp)
	(mM) =	(millimolar)
}


INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	SUFFIX K23
	USEION ca READ cai
	USEION k WRITE ik
	RANGE gkbar,gk,zinf,ik
}


PARAMETER {
	celsius=37	(degC)
	v		(mV)
	gkbar=.00039	(mho/cm2)	: Maximum Permeability
	cai = .04e-3	(mM)
	ek  = -85	(mV)
	dt		(ms)
	mon = 1
	zon = 1
}


ASSIGNED {
	ik		(mA/cm2)
	minf
	mexp
	zinf
	zexp
	gk
}

STATE {	m z }		: fraction of open channels

BREAKPOINT {
	SOLVE state
:	gk = gkbar*m*z*z
	ik = gkbar*m*z*z*(v - ek)
}
:UNITSOFF
:LOCAL fac

:if state_cagk is called from hoc, garbage or segmentation violation will
:result because range variables won't have correct pointer.  This is because
: only BREAKPOINT sets up the correct pointers to range variables.
PROCEDURE state() {	: exact when v held constant; integrates over dt step
	rate(v, cai)
	m = mon * (m + mexp*(minf - m))
	z = zon * (z + zexp*(zinf - z))
	VERBATIM
	return 0;
	ENDVERBATIM
}

INITIAL {
	rate(v, cai)
	m = minf
	z = zinf
}

FUNCTION alp(v (mV), ca (mM)) (1/ms) { :callable from hoc
	alp = 20/(ca*1000)
}

FUNCTION bet(v (mV)) (1/ms) { :callable from hoc
	bet = 0.075/exp((v+5)/10)
}

PROCEDURE rate(v (mV), ca (mM)) { :callable from hoc
	LOCAL a,b
	a = alp(v,ca)
	zinf = 1/(1+a)
	zexp = (1 - exp(-dt/10))
	b = bet(v)
	minf = 25/(25+b)
	mexp = (1 - exp(-dt*(25+b)))
}
:UNITSON
