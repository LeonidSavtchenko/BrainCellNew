TITLE inward rectifier potassium (Kir4) channel

COMMENT
This is kinetics of Kir4.1 channels


ENDCOMMENT
NEURON {
    SUFFIX kir4 			
    USEION k READ ko, ek WRITE ik	
    RANGE  ik, gkir, NormK
        
}

UNITS {
	(molar) = (1/liter)
    (mA) = (milliamp)
    (mV) = (millivolt)
    (mS)  = (millisiemens)
	(mM) =	(millimolar)
}

PARAMETER {
    v 		(mV)
    va1 = -14.83 (mV) 	
	va2 = -105.82 (mV) : 34 (mV)
	va3 = 19.23 (mV)
    gkir = 1.44e-02  (mS/cm2) 
    ek = -70 (mV)
    NormK = 0.81 
	
}

ASSIGNED {
    ik      (mA/cm2)
       
   
	ko      (mM)
}



BREAKPOINT {
        
        ik = (0.001)*gkir * ( v - ek*NormK - va1) *sqrt(((ko)/(1 (mM)))/(1+exp((v-ek*NormK-va2)/va3)))		: calculate ik 
		: printf("v: %g, ko: %g, va2: %g\n", v, ko, va2)
}

