COMMENT
Uses electroneutral, exponentially decaying IP3 source 
to emulate effect of activating bradykinin receptors on IP3.
Equivalent to approach used by Fink et al. 2000 
to represent bradykinin action.
ENDCOMMENT

NEURON {
  SUFFIX bkr
  USEION ip3 WRITE iip3 VALENCE 1
  NONSPECIFIC_CURRENT ix
  RANGE jbar, beta, j, i
  GLOBAL del
}

UNITS {
  (um)    = (micron)
  (molar) = (1/liter)
  (uM)    = (micromolar)
  (mA)	  = (milliamp)
  FARADAY = (faraday)  (coulomb)
}

PARAMETER {
  del (ms)  : time at which it starts

  k = 1.188e-3 (/ms) : k0

  jbar = 20.86 (uM um/s) : J0  flux at onset
  beta = 1 (1) : scale factor for local variation of bradykinin receptor density
}

ASSIGNED {
  jip3 (micro/um2 ms) : IP3 flux generated at membrane in micromoles/um2 ms
  iip3 (mA/cm2) : ip3 current
  ix   (mA/cm2) : to cancel out polarizing effect of the ip3 current
}

INITIAL {
  jip3 = 0
  iip3 = 0
  ix = 0
}

BREAKPOINT {
  at_time(del) : when it turns on
  at_time(del + (10/k)) : when to stop calculating very small exponentials

: produced at inner surface of membrane upon application of bradykinin
  if (t > del && t <= del + (10/k)) {
    jip3 = (1e-18)*beta*jbar*exp(-k*(t-del))
  }else{
    jip3 = 0
  }

  iip3 = -(1e8)*jip3*FARADAY
  ix = -iip3
}
