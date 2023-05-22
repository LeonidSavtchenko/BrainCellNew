
: CA1 pyramidal neuron to study INaP properties and repetitive firing (Uebachs et al. 2010)
: The file was downloaded from https://senselab.med.yale.edu/ModelDB/showmodel.cshtml?model=125152

UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)


    (molar) = (1/liter)
    (mM) = (millimolar)

    F = 96485 (coul)
    R = 8.3134 (joule/degC)
}

PARAMETER {
    v (mV)
    celsius 		(degC)
    PcalBar=0.00006622 (cm/s)
    ki=.00002 (mM)
    cai=5.e-5 (mM)
    cao = 10  (mM)
    q10m=11.45
    q10Ampl=2.1
}

NEURON {
    SUFFIX CAl
    USEION ca READ cai,cao WRITE ica
        RANGE PcalBar
        GLOBAL minf,taum
}

STATE {
    m
}

ASSIGNED {
    ica (mA/cm2)
        Pcal  (cm/s) 
        minf
        taum
}

INITIAL {
    rates(v)
    m = minf
}

UNITSOFF
BREAKPOINT {
    LOCAL qAmpl

    qAmpl = q10Ampl^((celsius - 21)/10)

    SOLVE states METHOD cnexp
    Pcal = qAmpl*PcalBar*m*m*h2(cai)
    ica = Pcal*ghk(v,cai,cao)
}

FUNCTION h2(cai(mM)) {
    h2 = ki/(ki+cai)
}

FUNCTION ghk(v(mV), ci(mM), co(mM)) (mV) {
    LOCAL a

    a=2*F*v/(R*(celsius+273.15)*1000)

    ghk=2*F/1000*(co - ci*exp(a))*func(a)
}

FUNCTION func(a) {
    if (fabs(a) < 1e-4) {
        func = -1 + a/2
    }else{
        func = a/(1-exp(a))
    }
}

FUNCTION alpm(v(mV)) {
    :TABLE FROM -150 TO 150 WITH 200
    alpm = 0.1967*(-1.0*(v-15)+19.88)/(exp((-1.0*(v-15)+19.88)/10.0)-1.0)
}

FUNCTION betm(v(mV)) {
    :TABLE FROM -150 TO 150 WITH 200
    betm = 0.046*exp(-(v-15)/20.73)
}

DERIVATIVE states {     
    rates(v)
    m' = (minf - m)/taum
}

PROCEDURE rates(v (mV)) { :callable from hoc
    LOCAL a, qm

    TABLE taum, minf FROM -150 TO 150 WITH 3000 :Mitti
    
    qm = q10m^((celsius - 22)/10)
    a = alpm(v)
    taum = 1/((a + betm(v))*qm)

    minf = 1/(1+exp(-(v+11)/5.7)) ^0.5 
}

UNITSON