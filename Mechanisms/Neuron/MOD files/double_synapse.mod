COMMENT
//****************************//
// Created by Alon Polsky 	//
//    apmega@yahoo.com		//
//		2002			//
//****************************//
ENDCOMMENT

TITLE double synapse

NEURON {
	POINT_PROCESS dsyn
	RANGE  i,gmax
	RANGE del,Tspike,Nspike
	NONSPECIFIC_CURRENT i
	RANGE tau1,tau2
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
	gmax=1	(nS)
	tau1=8	:180 	(ms)	:80:300
	tau2=2	(ms)	: 1 : 0.66 : 7 : 15

	del=30	(ms)
	Tspike=10	(ms)
	Nspike=1
}

ASSIGNED { 
	i (nA)  

}
STATE {
	A (nS)
	B (nS)
}

INITIAL {
      i=0 
	A=0
	B=0
}    

BREAKPOINT {  
	LOCAL count

	SOLVE state METHOD cnexp

	FROM count=0 TO Nspike-1 {
		IF(at_time(count*Tspike+del)){
			state_discontinuity( A, A+ 1)
			state_discontinuity( B, B+ 1)
		}
	}

	i=-gmax*(A-B)
   
	 
}

DERIVATIVE state {
	A'=-A/tau1
	B'=-B/tau2
}



