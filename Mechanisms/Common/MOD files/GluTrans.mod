COMMENT

The model of Glutamate  transporter.
is based on two papers, 

from the paper 

1. Zhang Z1, Tao Z, Gameiro A, Barcelona S, Braams S, Rauen T, Grewer C. 
Transport direction determines the kinetics of substrate transport by the glutamate transporter EAAC1.
Proc Natl Acad Sci U S A. 2007 Nov 13;104(46):18025-30. Epub 2007 Nov 8.

we determine the basic kinetic scheme for glutamate transporters, 

from the  paper
 
2. Bergles, D.E. & Jahr, C.E. 
Synaptic activation of glutamate transporters in hippocampal astrocytes. Neuron 19, 1297-1308 (1997).

we corrected the numerical values of the kinetic constants corresponding to the dynamics of glutamate transporters in astrocytes




ENDCOMMENT

NEURON {
    SUFFIX  GluTrans
    RANGE part, C1, C2, C3, C4, C5, C6
    GLOBAL k12, k21, k23, k32, k34, k43, k45, k54, k56, k65, k16, k61
    GLOBAL Nain, Naout, Kin, Kout, Gluin, charge 
    RANGE  itrans, Gluout, density, itransLog
    NONSPECIFIC_CURRENT itrans
}

UNITS {
    (l) = (liter)
    (nA) = (nanoamp)
    (mV) = (millivolt)
    (mA) = (milliamp)
    (pS) = (picosiemens)
    (umho) = (micromho)
    (mM) = (milli/liter)
    (uM) = (micro/liter)
    F = (faraday) (coulombs)
        PI      = (pi)       (1)
}

PARAMETER {	
    : Rates

    k12 = 20           (l /mM /ms)
    k21 = 0.1          (/ms)
    k23 = 0.015       (l /mM /ms)
    k32 = 0.5          (/ms)
    k34 = 0.2          (/ms)
    k43 = 0.6          (/ms)
    k45 = 4            (/ms)
    k54 = 10           (l /mM /ms)
    k56 = 1            (/ms) 
    k65 = 0.1          (l /mM /ms) 
    k16 = 0.0016          (l /mM /ms)
    k61 =  2e-4        (l /mM /ms)

    Nain = 15        (mM/l)
    Naout = 150   (mM/l)
    Kin = 120       (mM/l)
    Kout = 3        (mM/l)
    Gluin = 0.3      (mM/l)
    Gluout = 20e-6	(mM/l)

    density =1e12  : (/cm2) : 10000 per um2
    charge = 1.6e-19 (coulombs)
}

ASSIGNED {
    v	   (mV)		:  voltage
    itrans (mA/cm2)            : 
    surf   (cm2)
    volin  (liter)
    volout (liter)
    itransLog
}

STATE {
    : Transporter  states (all fractions)
            : 
    C1	(/cm2)	:  
    C2	(/cm2)	:  
    C3	(/cm2)	: 
    C4	(/cm2)	: 
    C5	(/cm2)	: 
    C6  (/cm2)
}

INITIAL {
    C1= 0.9074    
    C2= 0.0199    
    C3= 0.0435    
    C4= 0.0103    
    C5= 0.0142    
    C6= 0.0047
    volin = 1
    volout = 1
    surf = 1
}

BREAKPOINT {
    SOLVE kstates METHOD sparse
    
    itrans=-charge*density*(1e+006)*(0.6*(C1*k16*Kout*u(v,0.6)-C6*k61*Kin) -0.1*(C1*k12*Gluout*u(v,-0.1)-C2*k21)+0.5*(C2*k23*Naout*u(v,0.5)-C3*k32)+0.4*( C3*k34*u(v,0.4)-C4*k43)+0.6*(C5*k56*u(v,0.6)-C6*k65*Nain) )
    : itransLog=log(-itrans*(1e+006))

    :itrans=-charge*density*(1e+006)*(0.6*(C1*k16*Kout*u(v,0.6)-C6*k61*Kin) +0.4*( C3*k34-C4*k43)+0.6*(C5*k56*u(v,0.6)-C6*k65*Nain) )	  
}

KINETIC kstates {
            COMPARTMENT volin { Nain Kin Gluin}
            COMPARTMENT volout { Naout Kout Gluout}
            : COMPARTMENT surf { C1 C2 C3 C4 C5 C6}
        : surf=1 : !!!!!!!
        ~ C1   <-> C2      (Gluout*k12*u(v,-0.1), k21)
        ~ C2  <-> C3       (Naout*k23*u(v,0.5),k32)
        ~ C3 <-> C4	       (k34*u(v,0.4),k43)
        ~ C4 <-> C5 	   (k45,k54*Gluin)
        ~ C5 <-> C6	       (k56*u(v,0.6),k65*Nain)
        ~ C6  <-> C1       (Kin*k61, k16*u(v,0.6)*Kout)
        
    CONSERVE C1+C2+C3+C4+C5+C6= 1
}

FUNCTION u(x(mV), th) {
    u = exp(th*x/(2*(26.7 (mV))))
}
