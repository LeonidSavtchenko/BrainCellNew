NEURON {
	SUFFIX GAT1_current
	GLOBAL Temp
	RANGE  Egat, conductance, Nao, Nai, GABAo, GABAi, Clo, Cli
	NONSPECIFIC_CURRENT iGAT	:add to local membrane current but not affecting particular ion conc.
	}

UNITS {
	(mV) = (millivolt)
	(mA) = (milliamp)
	(mM) = (milli/liter)
	(mS) = (millisiemens)
	(mol) = (/liter)
	(mol-3) = (/liter3)
}

PARAMETER {	:define numbers & units of variables
	GasConstant=8.314 (joule/mol)
	Temp=298
	Faraday=96487 (coulomb/mol)
	conductance=0.1 (mS/cm2)
	Nai=1 (mM)
	Nao=140 (mM)
	Cli=1 (mM)
	Clo=144 (mM)
	GABAi=1 (mM)
	GABAo=0.001 (mM)
}

ASSIGNED {	:define units only; values will be calculated
	v (mV)
	iGAT (mA/cm2)
	Egat (mV)
}

BREAKPOINT {
	Egat = (GasConstant*1000(mV/volt)*Temp/Faraday)*log((Nao/Nai)^2*(GABAo/GABAi)*(Cli/Clo))
	iGAT = (0.001)*conductance*(v-Egat)
}
	