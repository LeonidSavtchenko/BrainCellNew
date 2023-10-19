TITLE  H-current that uses Na ions
: Updated to use Cvode by Yiota Poirazi 12/1/2005

NEURON {
	SUFFIX hcb
        RANGE  gbar,vhalf, K, taun, ninf, g, ihi 
	USEION hi READ ehi WRITE ihi VALENCE 1      

}

UNITS {
	(um) = (micrometer)
	(mA) = (milliamp)
	(uA) = (microamp)
	(mV) = (millivolt)
	(pmho) = (picomho)
	(mmho) = (millimho)
}

:INDEPENDENT {t FROM 0 TO 1 WITH 100 (ms)}

PARAMETER {              : parameters that can be entered when function is called in cell-setup
        ena    = 55    (mV)
        ehi     = -10   (mV)
	K      = 10.0   (mV)	
	gbar   = 0     (mho/cm2)  : initialize conductance to zero
	vhalf  = -90   (mV)       : half potential
}	


STATE {                : the unknown parameters to be solved in the DEs
	n
}

ASSIGNED {            
        v 
	ihi (mA/cm2)
	ninf
	taun (ms)
	g
}

        


INITIAL {               
	rates()	
	n = ninf
	g = gbar*n
	ihi = g*(v-ehi)
}


BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar*n 
	ihi = g*(v-ehi)  
}

DERIVATIVE states {
	rates()
        n' = (ninf - n)/taun
}

PROCEDURE rates() {  
 
 	if (v > -10) {
	   taun = 1
	} else {
           taun = 2*(1/(exp((v+145)/-17.5)+exp((v+16.8)/16.5)) + 10) 

	}  
         ninf = 1 - (1 / (1 + exp((vhalf - v)/K)))                  
}



