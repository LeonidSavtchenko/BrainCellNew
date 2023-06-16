NEURON {
	POINT_PROCESS Point3DRelease
	RANGE tau, Deff, InitConcentration
	RANGE Distance, K, NANN
	
		
}


DEFINE NANN1 40  
UNITS {
    (mol)   = (1)
	(nA) = (nanoamp)
	(mV) = (millivolt)
	(uS) = (microsiemens)
	(molar) = (1/liter)			: moles do not appear in units
	(mM)	= (millimolar)
	(um)  = (micron)
	(um3)  = (1e-15 liter)

}



PARAMETER {	
	Deff=1 (um2/ms):effective diffusion coefficient
    : Distance = 200 (um)
    InitConcentration = 5 (1)
	tau = 1 (ms) <1e-9,1e9>
	NANN = NANN1 
   	
}

LOCAL propagation

ASSIGNED {
 Distance  (um)
 K[NANN1] (mM)
 
}

STATE {
    Conc3D[NANN1] (mM)	
}

INITIAL {
	FROM i=0 TO NANN-1 {
		K[i] = 0
		Conc3D[i] = 0
		}
	}

BREAKPOINT {
	SOLVE state METHOD sparse
	FROM i=0 TO NANN-1 {
         K[i] = Conc3D[i]
		 }
	}

KINETIC state { : diffusion in 3D spherical coordinates 
    propagation= Deff/((Distance/(NANN-1))^2)
	~ Conc3D[0] <<    (-Conc3D[0]/tau) : Central boundary condition
	FROM i=1 TO NANN-2 {
	~ Conc3D[i] <<    (propagation*((Conc3D[i+1]-Conc3D[i-1])/(2+i) +(Conc3D[i+1]-2*Conc3D[i] + Conc3D[i-1])/2))
	}
    :~ Conc3D[NANN-1] <<  (0)	: zero flux boundary conditions at the edge
	Conc3D[NANN-1] = 0 : zero  boundary conditions at the edge
} 

NET_RECEIVE(weight (mM)) {
 LOCAL  NA,  Test, InitVolume, LocalInitConcentration

 InitVolume = (1e-15) * (4/3) * 3.14 *(Distance/(NANN-1))^3 
 NA = 6.02214076 * 1e23  (1) : Avogadro number
 :LocalInitConcentration = 1e3*NumberMolecules/NA/InitVolume
 
 :printf("InitVolume= %12.10f Con =%12.10f\n",InitVolume, LocalInitConcentration) 
 : Conc3D0 = Conc3D0 + 1000*LocalInitConcentration*weight

 state_discontinuity(Conc3D[0], Conc3D[0] + InitConcentration*weight)

	 
 
 
}
