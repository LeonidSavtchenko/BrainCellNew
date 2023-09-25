TITLE kdrglia
: Kalium delayed rectifier (AHP)
: twee gates met elk twee toestanden
: 
: uit: Traub et al.
: A branching dendritic model of a rodent CA3
: pyramidal neurone.
: Mechanism was donwloaded from https://senselab.med.yale.edu/modeldb/showmodel.cshtml?model=113446&file=/neuron-2008b/kdrglia.mod#tabs-2

UNITS {
    (molar) = (1/liter)
    (mV) =	(millivolt)
    (mA) =	(milliamp)
    (mM) =	(millimolar)
}

INDEPENDENT {t FROM 0 TO 1 WITH 100 (ms)}

NEURON {
    SUFFIX kdrglia
    USEION k READ ek WRITE ik
    RANGE gkbar, gk, ik, qk
    GLOBAL scaletaun, shiftn
}

UNITS {
    :FARADAY	= (faraday) (coulomb)
    FARADAY		= 96485.309 (coul)
    R = (k-mole) (joule/degC)
    PI		= (pi) (1)
}

PARAMETER {
    gkbar=0		(mho/cm2)	: default max. perm.
    scaletaun=1.5
    shiftn=50	(mV)
}

ASSIGNED { 
    ik	(mA/cm2)
    v	(mV)
    ek	(mV)
    dt	(ms)
    gk	(S/cm2)
    diam	(um)
}

STATE { n c qk }

BREAKPOINT {
    SOLVE kstate METHOD sparse
    gk = gkbar*n*n*n*n
    ik = gk*(v-ek)
    :n  = 1 - c
}

INITIAL {
    n=n_inf(v)
    c=1-n
    gk = gkbar*n*n*n*n
    ik = gk*(v-ek)
    qk=0
}

LOCAL a1,a2

KINETIC kstate {
    a1 = a_n(v)
    a2 = a_c(v)
    ~ c <-> n	(a1, a2)
    CONSERVE n + c = 1
    COMPARTMENT diam*diam*PI/4 { qk }

    ~ qk << (-ik*diam *PI*(1e4)/FARADAY )
}

FUNCTION a_n(v(mV)) {
    TABLE DEPEND scaletaun, shiftn FROM -150 TO 150 WITH 200
    a_n = scaletaun*0.016*(35.1-v-shiftn-70)/(exp((35.1-v-shiftn-70)/5)-1)
}

FUNCTION a_c(v(mV)) {
    TABLE DEPEND scaletaun, shiftn FROM -150 TO 150 WITH 200
    a_c = scaletaun*0.25*exp((20-v-shiftn-70)/40)
}

FUNCTION n_inf(v(mV)) {
    n_inf = a_n(v) / ( a_n(v) + a_c(v) )
}

FUNCTION window(v(mV)) {
    window=gkbar*n_inf(v)^4*(v-ek)
}