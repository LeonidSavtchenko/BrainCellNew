: $Id: MyExp2SynNMDA.mod,v 1.3 2010/12/13 21:34:42 samn Exp $ 
NEURON {
	POINT_PROCESS MyExp2SynNMDA
	NONSPECIFIC_CURRENT i, iNMDA
	RANGE tau1, tau2, e, i, iNMDA, s, sNMDA, tgtid, synid, r, tau1NMDA, tau2NMDA
}

UNITS {

	(nA) = (nanoamp)
	(mV) = (millivolt)
	(uS) = (microsiemens)
}

PARAMETER {

	tau1     =   0.1 (ms) <1e-9,1e9>
	tau2     =  10 (ms) <1e-9,1e9>	
	tau1NMDA = 15  (ms)
	tau2NMDA = 150 (ms)
	e        = 0	(mV)
	mg       = 1
	r        = 1
	
	tgtid    = -1
	synid    = -1
}

ASSIGNED {

	v       (mV)
	i       (nA)
	iNMDA   (nA)
	s       (1)
	sNMDA   (1)
	mgblock (1)
	factor  (1)
	factor2 (1)
}

STATE {

	A  (1)
	B  (1)
	A2 (1)
	B2 (1)
}

INITIAL {

	LOCAL tp
	if (tau1/tau2 > .9999) {
		tau1 = .9999*tau2
	}
	A = 0
	B = 0	
	tp = (tau1*tau2)/(tau2 - tau1) * log(tau2/tau1)
	factor = -exp(-tp/tau1) + exp(-tp/tau2)
	factor = 1/factor
	
	if (tau1NMDA/tau2NMDA > .9999) {
		tau1NMDA = .9999*tau2NMDA
	}
	A2 = 0
	B2 = 0	
	tp = (tau1NMDA*tau2NMDA)/(tau2NMDA - tau1NMDA) * log(tau2NMDA/tau1NMDA)
	factor2 = -exp(-tp/tau1NMDA) + exp(-tp/tau2NMDA)
	factor2 = 1/factor2
}

BREAKPOINT {
	
	SOLVE state METHOD cnexp
	: Jahr Stevens 1990 J. Neurosci
	mgblock = 1.0 / (1.0 + 0.28 * exp(-0.062(/mV) * v) )
	s     = B  - A
	sNMDA = B2 - A2
	i     = s     * (v - e) 
	iNMDA = sNMDA * (v - e) * mgblock
}

DERIVATIVE state {

	A'  = -A/tau1
	B'  = -B/tau2	
	A2' = -A2/tau1NMDA
	B2' = -B2/tau2NMDA
}

NET_RECEIVE(wAMPA(uS), srcgid) {
	
	if(r>=0){ : if r>=0, g = AMPA + NMDA*r
	
		A = A + factor*wAMPA
		B = B + factor*wAMPA
		
		A2 = A2 + factor2*wAMPA*r
		B2 = B2 + factor2*wAMPA*r
		
	}else{
	
		if(r>-1000){ : if r>-1, g = NMDA*r  
		
			A2 = A2 - factor2*wAMPA*r
			B2 = B2 - factor2*wAMPA*r
		
		}
		
		: if r<0 and r<>-1, g = 0
		
	}	
}
