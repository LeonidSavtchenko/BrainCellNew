TITLE K2 calcium-activated potassium current
: Calcium activated K channel.

COMMENT
This is adapted for CVODE (by Brown et al 2010) from the original file published in "An Active Membrane Model of the Cerebellar Purkinje Cell 1. Simulation of Current Clamp in Slice".
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
	SUFFIX K23cvode
	USEION ca READ cai
	USEION k WRITE ik
	RANGE gkbar,gk,ik
}


PARAMETER {
	celsius=37	(degC)
	v		(mV)
	gkbar=.00039	(mho/cm2)	: Maximum Permeability
	cai = .04e-3	(mM)
	ekcvodecvode  = -85	(mV)
	mon = 1
	zon = 1
}


ASSIGNED {
	ik		(mA/cm2)
	minf
	zinf
	gk
	tau 
	q10 
	alpha 
	beta 
	sum
}

STATE {	m z }		: fraction of open channels

BREAKPOINT {
	SOLVE state METHOD cnexp
:	gk = gkbar*m*z*z
	ik = gkbar*m*z*z*(v - ekcvodecvode)
}

:UNITSOFF


INITIAL {
	
	m = minf
	z = zinf
}


DERIVATIVE state { :callable from hoc
	
	alpha = 20/(cai*1000)
	beta = 0.075/exp((v+5)/10)
	
	zinf = 1/(1+alpha)
	tau= 10	
	z' = zon * (zinf-z)/tau      
		
	minf = 25/(25+beta)
	tau= 1/(25+beta)
	m' = mon * (minf-m)/tau      
}

:UNITSON
