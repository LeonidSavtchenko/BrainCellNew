: Linear kineticks of potassium pumping. 2018 Savtchenko et al.
TITLE kpump

NEURON {
	SUFFIX kpump
	USEION k READ  ki, ko WRITE ik	
	RANGE Kp, Krest 
}
UNITS {
    (molar) = (1/liter)
    (mV) =	(millivolt)    
    (mM) =	(millimolar)
	(mA) = (milliamp)
	
}

PARAMETER {
	Kp = 0.1 (mA/cm2)
	Krest = 110 (mM)
	
}

ASSIGNED {
	
	ik (mA/cm2)
    ki       (mM)	
	ko       (mM)
}

BREAKPOINT {

	ik = Kp*(ki/Krest - 1)

}

