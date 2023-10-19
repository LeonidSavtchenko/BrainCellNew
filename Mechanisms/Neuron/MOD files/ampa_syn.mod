COMMENT
//****************************//
// Created by Alon Polsky 	//
//    apmega@yahoo.com		//
//		2002			//
//****************************//
ENDCOMMENT

TITLE AMPA synapse

NEURON {
	POINT_PROCESS ampa_m
	NONSPECIFIC_CURRENT i
	RANGE tau,e,gw
	RANGE del,Tspike,Nspike
}

UNITS {
        (nS) = (nanosiemens)
        (nA) = (nanoamp)
        (mV) = (millivolt)
}

PARAMETER {
	tau=	5	: 1.1 	(ms)
	gw=0.01	(nS):weight of synapse
	e=0(mV)
	del=30	(ms)
	Tspike=10	(ms)
	Nspike=1
}

ASSIGNED {
	v (mV)
	i (nA)
}

STATE { g (nS) }

INITIAL { g= 0}

BREAKPOINT {
	LOCAL count

	SOLVE state METHOD cnexp

	FROM count=0 TO Nspike-1 {
		IF(at_time(count*Tspike+del)){
			state_discontinuity( g, g+ gw)
		}
	}

	i= (1e-3)*g* (v- e)
}

DERIVATIVE state {
	g'=-g/tau  
}

