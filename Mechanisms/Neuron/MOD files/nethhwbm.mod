TITLE nethhwbm.mod   interneuron sodium, potassium, and leak channels
 
COMMENT

 This file is based on the original hh.mod file (see original comment
 below). It was modified to match the model that was used in the
 simulations of Wang and Buzsaki (1996, J. Neurosci. 16).

 ***************************************************************************
 This is the original Hodgkin-Huxley treatment for the set of sodium, 
  potassium, and leakage channels found in the squid giant axon membrane.
  ("A quantitative description of membrane current and its application 
  conduction and excitation in nerve" J.Physiol. (Lond.) 117:500-544 (1952).)
 Membrane voltage is in absolute mV and has been reversed in polarity
  from the original HH convention and shifted to reflect a resting potential
  of -65 mV.
 Remember to set celsius=6.3 (or whatever) in your HOC file.
 See squid.hoc for an example of a simulation using this model.
 SW Jaslove  6 March, 1992
 ***************************************************************************

 changes:

  - m is substituted by it"s steady state value: m_inf - see 'BREAKPOINT'
  {as a result mtau is not needed, 'minf' is removed from
  GLOBAL declaration and 'm' is included in the RANGE var list
  otherwise it will be handled as a GLOBAL var and will not be
  evaluated separately for the 'sections'; for 'h' an 'n' this 
  is not a problem}

  - for h and n alpha and beta values are multiplied by 5 
  (see factor "Phi" in the W&B model)

  - USEION removed as we don't want to deal with ions and set eNa and
  eK directly. Rev potentials 'egna' and 'egk' are in the PARAMETERS
  list
    
  - temp: set to 6.3 Celsius, alpha and beta values are set/manipulated
  directly to simulate characteristic firing pattern

  I. Vida, Nov. 2000

  ***************************************************************************
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}

? interface

NEURON {
        SUFFIX hh_wbm
        NONSPECIFIC_CURRENT ina,ik,il

        RANGE gnabar,gna,egna,m, gkbar,gk,egk, gl,el
	GLOBAL hinf, ninf, htau, ntau

}
 
PARAMETER {
        gnabar = .035 (mho/cm2)	<0,1e9>
	egna	= 55 (mV)	
        gkbar = .009 (mho/cm2)	<0,1e9>
	egk	= -90 (mV)	
        gl = 0.000062 (mho/cm2)	<0,1e9>
        el = -65 (mV)
		:  -72.485
	
}
 
STATE {
        m h n
}
 
ASSIGNED {
        v (mV)
	celsius (degC)

	gna (mho/cm2)
        ina (mA/cm2)
	gk (mho/cm2)
        ik (mA/cm2)
        il (mA/cm2)
        minf hinf ninf
	htau (ms) ntau (ms)
}
 
LOCAL mexp, hexp, nexp        
 
? currents
BREAKPOINT {
        SOLVE states METHOD cnexp
	m = minf
        gna = gnabar*m*m*m*h
	ina = gna*(v - egna)
        gk = gkbar*n*n*n*n
	ik = gk*(v - egk)      
        il = gl*(v - el)
}
 
 
INITIAL {
	rates(v)
	m = minf
	h = hinf
	n = ninf
}

? states
DERIVATIVE states {  
        rates(v)
        h' = (hinf-h)/htau
        n' = (ninf-n)/ntau
}
 
LOCAL q10


? rates
PROCEDURE rates(v(mV)) {  :Computes rate and other constants at current v.
                          :Call once from HOC to initialize inf at resting v.
		      
        LOCAL  alpha, beta, sum
        TABLE minf, hinf, htau, ninf, ntau DEPEND celsius FROM -100 TO 100 WITH 200


UNITSOFF
        q10 = 3^((celsius - 6.3)/10)

               :"m" sodium activation system
        alpha = .1 * vtrap(-(v+35),10)
        beta =  4 * exp(-(v+60)/18)
        sum = alpha + beta
        minf = alpha/sum

                :"h" sodium inactivation system
        alpha =.35 * exp(-(v+58)/20)
        beta = 5 / (exp(-(v+28)/10) + 1)
        sum = alpha + beta
	htau = 1/(q10*sum)
        hinf = alpha/sum

                :"n" potassium activation system
        alpha =.05*vtrap(-(v+34),10) 
        beta = .625*exp(-(v+44)/80)
	sum = alpha + beta
        ntau = 1/(q10*sum)
        ninf = alpha/sum
}
 
FUNCTION vtrap(x,y) {  :Traps for 0 in denominator of rate eqns.
        if (fabs(x/y) < 1e-6) {
                vtrap = y*(1 - x/y/2)
        }else{
                vtrap = x/(exp(x/y) - 1)
        }
}
 
UNITSON
