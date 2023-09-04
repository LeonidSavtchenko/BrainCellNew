: the dynamics mechanism of the FRAP is developed by Savchenko and others. 2018

NEURON {
    SUFFIX FRAP
    USEION frapion READ frapiono, frapioni WRITE frapioni VALENCE 1

    GLOBAL vol, Buffer0
    RANGE frapion0, Alpha
}

DEFINE NANN  4

UNITS {
    (molar) = (1/liter)
    (mM)	= (millimolar)
    (um)	= (micron)
    (mA)	= (milliamp)
    FARADAY = (faraday)	 (10000 coulomb)
    PI	= (pi) (1)
}

PARAMETER {
    DFree = 0.3	(um2/ms)
    frapion0 = 50e-6 (mM)
    diam		(um)
    frapiono		(mM)
    Alpha = 0.0 (1/ms)
}

ASSIGNED {
    frapioni		(mM)
    vol[NANN]	(1)	: gets extra cm2 when multiplied by diam^2
}

STATE {
    frapion[NANN]	(mM) : frapion[0] is equivalent to frapioni
    frapionBuffer[NANN]  (mM)
    Buffer[NANN]    (mM)
}

BREAKPOINT {
    SOLVE state METHOD sparse
}

LOCAL coord_done

INITIAL {
    if (coord_done == 0) {
        coord_done = 1
        coord()
    }
    : note Buffer gets set to Buffer0 automatifrapionlly
    : and frapionBuffer gets set to 0 (Default value of frapionBuffer0) as well
    frapioni = frapion0
    FROM i=0 TO NANN-1 {
        frapion[i] = frapioni
    }
}

LOCAL frat[NANN] 	: gets extra cm when multiplied by diam

PROCEDURE coord() {
    LOCAL r, dr2
    : cylindrical coordinate system  with constant annuli thickness to
    : center of cell. Note however that the first annulus is half thickness
    : so that the concentration is second order correct spatially at
    : the membrane or exact edge of the cell.
    : note frapion[0] is at edge of cell
    :      frapion[NANN-1] is at center of cell
    r = 1/2					:starts at edge (half diam)
    dr2 = r/(NANN-1)/2			:half thickness of annulus
    vol[0] = 0
    frat[0] = 2*r
    FROM i=0 TO NANN-2 {
        vol[i] = vol[i] + PI*(r-dr2/2)*2*dr2	:interior half
        r = r - dr2
        frat[i+1] = 2*PI*r/(2*dr2)	:exterior edge of annulus
                    : divided by distance between centers
        r = r - dr2
        vol[i+1] = PI*(r+dr2/2)*2*dr2	:outer half of annulus
    }
}

KINETIC state {
    COMPARTMENT i, diam*diam*vol[i] {frapion}
    LONGITUDINAL_DIFFUSION j, DFree*diam*diam*vol[j] {frapion}

    FROM i=0 TO NANN-2 {
        ~ frapion[i] <-> frapion[i+1] (DFree*frat[i+1], DFree*frat[i+1])
        ~ frapion[i] << (-Alpha*diam*diam*frapion[i])
    }

    frapioni = frapion[0]
}