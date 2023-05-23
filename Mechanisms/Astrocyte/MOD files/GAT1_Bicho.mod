: TITLE GAT1

NEURON {
	SUFFIX GAT1_Bicho
	:GLOBAL Temp, k12, k120, k21, k210, k23, k230, k32, k320, k34, k340, k43, k430, k45, k450, k54, k540, k56, k560, k65, k650, k67, k670, k76, k760, k78, k780, k87, k870, k81, k810, k18, k180, k16, k160, k61, k610, z12, z23, z34, z45, z56, z67, z78, z81, z61
	RANGE  Nai, Nao, Cli, Clo, GABAi, GABAo, density, iGABA1
	NONSPECIFIC_CURRENT iGABA	:add to local membrane current but not affecting particular ion conc.
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
	GasConstant=8.314 (joule/mol/degC)
	Temp=25 (degC)
	Faraday=96487 (coulomb/mol)
	pi=3.1415926
	Nai=10 (mM)
	Nao=145 (mM)
	Cli=5 (mM)
	Clo=130 (mM)
	GABAi=1 (mM)
	GABAo=1e-5 (mM)
	density=1.10895e-12 (mol/cm2)
	k120=0.0005 (/ms /mM)
	k210=0.01 (/ms)
	k230=0.01 (/ms /mM)
	k320=0.1 (/ms)
	k340=10 (/ms /mM)
	k430=1 (/ms)
	k450=1 (/ms)
	k540=1 (/ms)
	k560=0.015 (/ms /mM3)
	k650=0.3 (/ms)
	k160=0.005 (/ms)
	k610=0.005 (/ms)
	k670=0.2 (/ms /mM)
	k760=20 (/ms)
	k780=0.4 (/ms)
	k870=0.02 (/ms)
	k810=50 (/ms)
	k180=10 (/ms /mM)
	z12=0.9
	z23=0.3
	z34=0
	z45=0.2
	z56=0.2
	z61=-0.8
	z67=0.01
	z78=0.005
	z81=-0.215
	
}

ASSIGNED {	:define units only; values will be calculated
	v (mV)
	iGABA (mA/cm2)
	iGABA1 (mA)
	k12 (/ms /mM)
	k21 (/ms)
	k23 (/ms /mM)
	k32 (/ms)
	k34 (/ms /mM)
	k43 (/ms)
	k45 (/ms)
	k54 (/ms)
	k56 (/ms /mM3)
	k65 (/ms)
	k16 (/ms)
	k61 (/ms)
	k67 (/ms /mM)
	k76 (/ms)
	k78 (/ms)
	k87 (/ms)
	k81 (/ms)
	k18 (/ms /mM)
}

STATE {
	 A AN AN2 AN2G BN2G B BC AC
}

BREAKPOINT {
	SOLVE kin METHOD sparse
	k12=k120*u(v,-z12)
	k21=k210*u(v,z12)
	k23=k230*u(v,-z23)
	k32=k320*u(v,z23)
	k34=k340*u(v,-z34)
	k43=k430*u(v,z34)
	k45=k450*u(v,-z45)
	k54=k540*u(v,z45)
	k56=k560*u(v,-z56)
	k65=k650*u(v,z56)
	k16=k160*u(v,z61)
	k61=k610*u(v,-z61)
	k67=k670*u(v,-z67)
	k76=k760*u(v,z67)
	k78=k780*u(v,-z78)
	k87=k870*u(v,z78)
	k81=k810*u(v,-z81)
	k18=k180*u(v,z81)
	iGABA=-(1e+06)*Faraday*density*(z12*(A*k12*Nao-AN*k21)+z23*(AN*k23*Nao-AN2*k32)+z34*(AN2*k34*GABAo-AN2G*k43)+z45*(AN2G*k45-BN2G*k54)+z56*(BN2G*k56*Nai*Nai*GABAi-B*k65)+z61*(B*k61-A*k16)+z67*(B*k67*Clo-BC*k76)+z78*(BC*k78-AC*k87)+z81*(AC*k81-A*k18*Cli))
	iGABA1=iGABA*(4e-6(cm2)*pi)
}

INITIAL {
	SOLVE kin STEADYSTATE sparse
}

KINETIC kin {
	~ A <-> AN	(k12*Nao, k21)
	~ AN <-> AN2 (k23*Nao, k32)
	~ AN2 <-> AN2G (k34*GABAo, k43)
	~ AN2G <-> BN2G (k45, k54)
	~ BN2G <-> B (k56*Nai*Nai*GABAi, k65)
	~ B <-> A (k61, k16)
	~ B <-> BC (k67*Clo, k76)
	~ BC <-> AC (k78, k87)
	~ A <-> AC (k18*Cli, k81)
	CONSERVE A+AN+AN2+AN2G+BN2G+B+BC+AC=1
}

FUNCTION u(v(mV), z) {
	LOCAL temp
	temp = 2*GasConstant*1000(mV/volt)*(273 (degC)+Temp)
	u = exp(z*Faraday*v/temp)
}