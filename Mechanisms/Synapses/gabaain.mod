TITLE minimal model of GABAa receptors

COMMENT
-----------------------------------------------------------------------------

	Minimal kinetic model for GABA-A receptors
	==========================================

  Model of Destexhe, Mainen & Sejnowski, 1994:

	(closed) + T <-> (open)

  The simplest kinetics are considered for the binding of transmitter (T)
  to open postsynaptic receptors.   The corresponding equations are in
  similar form as the Hodgkin-Huxley model:

	dr/dt = alpha * [T] * (1-r) - beta * r

	I = gmax * [open] * (V-Erev)

  where [T] is the transmitter concentration and r is the fraction of 
  receptors in the open form.

  If the time course of transmitter occurs as a pulse of fixed duration,
  then this first-order model can be solved analytically, leading to a very
  fast mechanism for simulating synaptic currents, since no differential
  equation must be solved (see Destexhe, Mainen & Sejnowski, 1994).

-----------------------------------------------------------------------------

  Based on voltage-clamp recordings of GABAA receptor-mediated currents in rat
  hippocampal slices (Otis and Mody, Neuroscience 49: 13-32, 1992), this model
  was fit directly to experimental recordings in order to obtain the optimal
  values for the parameters (see Destexhe, Mainen and Sejnowski, 1996).

-----------------------------------------------------------------------------

  This mod file includes a mechanism to describe the time course of transmitter
  on the receptors.  The time course is approximated here as a brief pulse
  triggered when the presynaptic compartment produces an action potential.
  The pointer "pre" represents the voltage of the presynaptic compartment and
  must be connected to the appropriate variable in oc.

-----------------------------------------------------------------------------

  See details in:

  Destexhe, A., Mainen, Z.F. and Sejnowski, T.J.  An efficient method for
  computing synaptic conductances based on a kinetic model of receptor binding
  Neural Computation 6: 10-14, 1994.  

  Destexhe, A., Mainen, Z.F. and Sejnowski, T.J.  Kinetic models of 
  synaptic transmission.  In: Methods in Neuronal Modeling (2nd edition; 
  edited by Koch, C. and Segev, I.), MIT press, Cambridge, 1996.


  Written by Alain Destexhe, Laval University, 1995

-----------------------------------------------------------------------------
ENDCOMMENT

NEURON {
	POINT_PROCESS GABAain
	RANGE R, g, gmax 
	NONSPECIFIC_CURRENT i
	GLOBAL Cmax, Cdur, Alpha, Beta, Erev, Rinf, Rtau
	RANGE i
}

UNITS {
	(nA) = (nanoamp)
	(mV) = (millivolt)
	(umho) = (micromho)
	(mM) = (milli/liter)
}

PARAMETER {

	Cmax	= 1	(mM)		: max transmitter concentration
	Cdur	= 1	(ms)		: transmitter duration (rising phase)
	Alpha	= 5	(/ms mM)	: forward (binding) rate
	Beta	= 0.18	(/ms)		: backward (unbinding) rate - after autogabain validation
	Erev	= -80	(mV)		: reversal potential
}


ASSIGNED {
	v		(mV)		: postsynaptic voltage
	i 		(nA)		: current = g*(v - Erev)
	g 		(umho)		: conductance
	Rinf				: steady state channels open
	Rtau		(ms)		: time constant of channel binding
        synon
       	gmax
}

STATE {Ron Roff}



INITIAL {

	Rinf = Cmax*Alpha / (Cmax*Alpha + Beta)
	Rtau = 1 / ((Alpha * Cmax) + Beta)
	synon = 0
}

BREAKPOINT {
	SOLVE release METHOD cnexp
	g = (Ron + Roff)*1(umho)
	i = g*(v - Erev)
}

DERIVATIVE release {
	Ron' = (synon*Rinf - Ron)/Rtau
	Roff' = -Beta*Roff
}

: following supports both saturation from single input and
: summation from multiple inputs
: if spike occurs during CDur then new off time is t + CDur
: ie. transmitter concatenates but does not summate
: Note: automatic initialization of all reference args to 0 except first

NET_RECEIVE(weight, on, nspike, r0, t0 (ms)) {
	: flag is an implicit argument of NET_RECEIVE and  normally 0
        if (flag == 0) { : a spike, so turn on if not already in a Cdur pulse
		nspike = nspike + 1
		if (!on) {
			r0 = r0*exp(-Beta*(t - t0))
			t0 = t
			on = 1
			synon = synon + weight
			state_discontinuity(Ron, Ron + r0)
			state_discontinuity(Roff, Roff - r0)
		}
		: come again in Cdur with flag = current value of nspike
		net_send(Cdur, nspike)
        }
	if (flag == nspike) { : if this associated with last spike then turn off
		r0 = weight*Rinf + (r0 - weight*Rinf)*exp(-(t - t0)/Rtau)
		t0 = t
		synon = synon - weight
		state_discontinuity(Ron, Ron - r0)
		state_discontinuity(Roff, Roff + r0)
		on = 0
	}
gmax=weight
}

