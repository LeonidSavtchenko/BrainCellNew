COMMENT
//****************************//
// Created by Alon Polsky 	//
//    apmega@yahoo.com		//
//		2002			//
//****************************//








ENDCOMMENT

TITLE NMDA synapse

NEURON {
	POINT_PROCESS nmda_m
	USEION mg READ mgo VALENCE 2
	USEION ca  WRITE ica VALENCE 2
	RANGE e, g, i,gw,gmax
	RANGE del,Tspike,Nspike
	NONSPECIFIC_CURRENT i
	GLOBAL n, gama,tau1,tau2
}

UNITS {
	(nA) 	= (nanoamp)
	(mV)	= (millivolt)
	(nS) 	= (nanomho)
	(mM)    = (milli/liter)
        F	= 96480 (coul)
        R       = 8.314 (volt-coul/degC)

}

PARAMETER {
		:receptor- each 50pS
	gmax=14	(nS)
	e= 0.0	(mV)
	tau1=150	:180 	(ms)	:80:300
	tau2=20	(ms)	: 1 : 0.66 : 7 : 15
	n=0.3 	(/mM)	:0.33
	gama=0.07 	(/mV) :0.06
	gw=14		(nS):weight of synapse
	v		(mV)
	mgo		(mM)
	del=30	(ms)
	Tspike=10	(ms)
	Nspike=1
}

ASSIGNED { 
	i (nA)  
	g (nS)
	ica (nA)	
}
STATE {
	A (nS)
	B (nS)
}

INITIAL {
      g=0 
	A=0
	B=0
}    

BREAKPOINT {  
	LOCAL count

	SOLVE state METHOD cnexp

	FROM count=0 TO Nspike-1 {
		IF(at_time(count*Tspike+del)){
			state_discontinuity( A, A+ gw)
			state_discontinuity( B, B+ gw)
		}
	}

	g=gmax*(A-B)/(1+n*exp(-gama*v) )
   
	i =(1e-3)* g * (v-e)
	ica=i/10
}

DERIVATIVE state {
	A'=-A/tau1
	B'=-B/tau2
}



