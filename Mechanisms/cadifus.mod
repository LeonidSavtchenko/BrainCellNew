COMMENT
This file was modified from basic cadifus.mod from Chapter 9 Hines and Carnevale NEURON
the computation of fluorescence was added 
two types
The fluorescence relates to the cocnetration of bound mobile buffer
fluo = cabufm[0]

fluoNew = (BufferAlpha * cabufm[0] + ca[0] - BufferAlpha*(TBufm - bufm_0) - cai0)/(BufferAlpha*(TBufm - bufm_0) + cai0)



Calcium ion accumulation with radial and longitudinal diffusion, pump, 
and SERCA.

Diffusion geometry based on Ca accumulation models from chapter 9 
of The NEURON Book.

Mechanistic details of calcium pump and SERCA as described by Fink et al. 2000.

alpha = relative abundance of SERCA.

Current implementation assumes that ip3i is uniform across all compartments, 
i.e. that radial diffusion of IP3 is very fast compared to the diffusion of 
Ca and the mechanisms that drive Ca to change with time.
Indeed, simulations reveal this to be the case--IP3 concentration 
remains nearly identical across section diameters.
There are slight differences in the soma during the fast rising phase 
of the IP3 transient, but these resolve quickly.

Consequently, coupling between the shells of the ip3cum mechanism 
and the SERCA channels in the shells of this mechanism 
is a complexity that can be omitted--all shells of this mechanism
can use the concentration of IP3 in the outermost shell of the 
ip3cum mechanism, and discoverable by any mechanism that has a 
USEION ip3 READ ip3i VALENCE 1

The dynamics of the ip3 is defined by the paper 
Glutamate-evoked Ca2+ oscillations in single astrocytes (De Pitta et al. 2009) (Manninen et al 2017)
https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=223269#tabs-2

modification 23/05/2018


-------------
SERCA channel
-------------

jchnl = alpha * jmax * (1-(ca/caer)) * ( (ip3/(ip3+Kip3)) * (ca/(ca+Kact)) * h)^3
note:  jchnl is release from SER to cytoplasm
jmax = 3500 uM/s
caer = 400 uM
Kip3 = 0.8 uM
Kact = 0.3 uM

h' = kon * (Kinh - (ca + Kinh)*h)
kon = 2.7 /uM-s
Kinh = 0.2 uM

Recasting h in terms of kinetic scheme--
From RHS of ODE for h'
hinf = Kinh/(ca+Kinh) = alpha/(alpha+beta)
tauh = 1/(kon*(ca+Kinh)) = 1/(alpha+beta)
So alpha = kon*Kinh and beta = kon*ca

----------
SERCA pump
----------

jpump = alpha * vmax*ca^2 / (ca^2 + Kp^2)
note:  jpump is uptake from cytoplasm into SER

vmax = 3.75 uM/s
Kp = 0.27 uM

----------
SERCA leak
----------

jleak = alpha * L*(1 - (Ca/caer))
note:  jleak is leak from SER to cytoplasm

L = 0.1 uM/s nominally,
but adjusted so that
jchnl + jpump + jleak = 0
when
ca = 0.05 uM and h = Kinh/(ca + Kinh)

ENDCOMMENT

NEURON {
    SUFFIX cadifus
    USEION ca READ cao, cai, ica WRITE cai, ica
    USEION ip3 READ ip3i  WRITE ip3i VALENCE 1 
    RANGE ica_pmp, cai0, fluo, fluoNew
    RANGE alpha : relative abundance of SERCA
	RANGE Dip3, Ip3init, modelStim, v_bar_beta
    GLOBAL vrat, TBufs, TBufm, BufferAlpha
    : vrat must be GLOBAL--see INITIAL block
    : however TBufs and TBufm may be RANGE
}

DEFINE Nannuli 4

UNITS {
    (mol)   = (1)
    (molar) = (1/liter)
    (uM)    = (micromolar)
    (mM)    = (millimolar)
    (um)    = (micron)
    (mA)    = (milliamp)
    FARADAY = (faraday)  (10000 coulomb)
    PI      = (pi)       (1)
}

PARAMETER {

    Dip3 = 0.1 (um2/ms)
    Ip3init = 0.0000250 (mM)
    Currentip3 = 0.0  (mA/cm2)


    cai0 = 50e-6 (mM)
    fluo = 0     (mM) 
    fluoNew = 0  
    DCa   = 0.22 (um2/ms) : Fink et al. 2000 0.22
    BufferAlpha = 100
	
	
	modelStim = 0 (mM)
	kappa_delta = 1.5e-3 (mM) 
    K_3 = 1e-3 (mM)
    K_pi = 0.6e-3 (mM) 
    K_D = 0.7 (mM) 
   
    K_p = 10e-3 (mM)         
    K_PLCdelta = 0.1e-3 (mM)
    K_R = 1.3e-3       (mM)
    r_bar_5P = 0.04e-3 (/ms) 
  
  
    v_bar_3K = 2e-6 (mM/ms)
    v_bar_beta = 0.2e-6  (mM/ms)
    v_bar_delta = 0.02e-6  (mM/ms)
	
	

: Bufs--endogenous, stationary buffer
    TBufs = 0.450 (mM) : total Bufs
    : just make kfs fast, and calculate krs as kfs*KDs
    kfs = 1000 (/mM-ms) : try these for now
    KDs = 10 (uM)

: Bufm--fura2, for bradykinin experiments
    TBufm = 0.075 (mM) : total Bufm
    : just make kfm fast, and calculate krm as kfm*KDm
    kfm = 1000 (/mM-ms) : try these for now
    KDm = 0.24 (uM)
    DBufm = 0.050 (um2/ms)

: Bufm--calcium green, for uncaging experiments
    :  TBufm = 0.075 (mM) : total Bufm
    : just make kfm fast, and calculate krm as kfm*KDm
    :  kfm = 1000 (/mM-ms) : try these for now
    :  KDm = 0.26 (/ms)
    :  DBufm = 0.0184 (um2/ms)

    : to eliminate ca pump, set gamma to 0 in hoc
    cath = 0.2e-3 (mM) : threshold for ca pump activity
    gamma = 8 (um/s) : ca pump flux density

: SERCA params
    alpha = 1 (1) : relative abundance of SERCA mechanism as per Fig. 3

: SERCA pump
    : jpump = alpha * vmax*ca^2 / (ca^2 + Kp^2)
    : jpump is uptake from cytoplasm into SER
    vmax = 3.75e-6 (mM/ms)
    Kp = 0.27e-3 (mM)

: SERCA channel
    : jchnl is release from SER to cytoplasm
    jmax = 3.5e-3 (mM/ms)
    caer = 0.400 (mM)
    Kip3 = 0.8e-3 (mM)
    Kact = 0.3e-3 (mM)
    kon = 2.7 (/mM-ms)
    Kinh = 0.2e-3 (mM)

: SERCA leak -- no fixed parameter other than caer
: does have an adjustable parameter L

}

ASSIGNED {
    diam      (um)
    ica       (mA/cm2)
    ica_pmp   (mA/cm2)
    ica_pmp_last   (mA/cm2)
    parea     (um)     : pump area per unit length

    sump      (mM)

    cai       (mM)
    cao       (mM)
    vrat[Nannuli]  (1) : dimensionless
                        : numeric value of vrat[i] equals the volume 
                        : of annulus i of a 1um diameter cylinder
                        : multiply by diam^2 to get volume per um length

    bufs_0 (mM)
    bufm_0 (mM)

  :  ip3i   (mM)

    L[Nannuli] (mM/ms) : 0.1e-6 mM/ms nominally, but adjusted so that
    : jchnl + jpump + jleak = 0  when  ca = 0.05 uM and h = Kinh/(ca + Kinh)
}

CONSTANT { volo = 1e10 (um2) }

STATE {
    : ca[0] is equivalent to cai
    : ca[] are very small, so specify absolute tolerance
    : let it be ~1.5 - 2 orders of magnitude smaller than baseline level
    ca[Nannuli]       (mM) <1e-7>
    bufs[Nannuli]    (mM) <1e-3>
    cabufs[Nannuli]  (mM) <1e-7>
    bufm[Nannuli]    (mM) <1e-4>
    cabufm[Nannuli]  (mM) <1e-8>
    hc[Nannuli]
    ho[Nannuli]
	ip3i (mM) <1e-10>
}

BREAKPOINT {
    SOLVE state METHOD sparse
    ica_pmp_last = ica_pmp
    ica = ica_pmp
}

LOCAL factors_done, jx

INITIAL {
	ip3i=Ip3init
    if (factors_done == 0) {  : flag becomes 1 in the first segment
        factors_done = 1       :   all subsequent segments will have
        factors()              :   vrat = 0 unless vrat is GLOBAL
    }

    cai = cai0

    bufs_0 = KDs*TBufs/(KDs + (1000)*cai0)
    bufm_0 = KDm*TBufm/(KDm + (1000)*cai0)

    FROM i=0 TO Nannuli-1 {
        ca[i] = cai
        bufs[i] = bufs_0
        cabufs[i] = TBufs - bufs_0
        bufm[i] = bufm_0
        cabufm[i] = TBufm - bufm_0
    }

    sump = cath
    parea = PI*diam

    : reconsider and revise initialization comments
    ica=0
    ica_pmp = 0
    ica_pmp_last = 0
    : If there is a voltage-gated calcium current, 
    : this is almost certainly the wrong initialization. 
    : In such a case, first do an initialization run, then use SaveState
    : On subsequent runs, restore the initial condition from the saved states.

    FROM i=0 TO Nannuli-1 {
        ho[i] = Kinh/(ca[i]+Kinh)
        hc[i] = 1-ho[i]

        : jx = jp + jc
        : choose L so that jl = -jx
        : jl = L*(1 - (ca[i]/caer))
        : jp = (-vmax*ca[i]^2 / (ca[i]^2 + Kp^2))
        : jc = jmax*(1-(ca[i]/caer)) * ( (ip3i/(ip3i+Kip3)) * (ca[i]/(ca[i]+Kact)) * ho[i] )^3
        jx = (-vmax*ca[i]^2 / (ca[i]^2 + Kp^2))
        jx = jx + jmax*(1-(ca[i]/caer)) * ( (ip3i/(ip3i+Kip3)) * (ca[i]/(ca[i]+Kact)) * ho[i] )^3
        L[i] = -jx/(1 - (ca[i]/caer))
    }
}

LOCAL frat[Nannuli]  : scales the rate constants for model geometry

PROCEDURE factors() {
    LOCAL r, dr2
    r = 1/2                 : starts at edge (half diam)
    dr2 = r/(Nannuli-1)/2   : full thickness of outermost annulus,
                            : half thickness of all other annuli
    vrat[0] = 0
    frat[0] = 2*r

    FROM i=0 TO Nannuli-2 {
        vrat[i] = vrat[i] + PI*(r-dr2/2)*2*dr2  : interior half
        r = r - dr2
        frat[i+1] = 2*PI*r/(2*dr2)  : outer radius of annulus
                                    : div by distance between centers
        r = r - dr2
        vrat[i+1] = PI*(r+dr2/2)*2*dr2  : outer half of annulus
    }
}

LOCAL dsq, dsqvol, K_gamma, v_3K, v_delta, v_glu   : can't define local variable in KINETIC block
                    :   or use in COMPARTMENT statement

KINETIC state {
    COMPARTMENT i, diam*diam*vrat[i] {ca bufs cabufs bufm cabufm sump}
    COMPARTMENT volo {cao}
	COMPARTMENT PI*diam*diam/4 {ip3i}
    LONGITUDINAL_DIFFUSION i, DCa*diam*diam*vrat[i] {ca}
    LONGITUDINAL_DIFFUSION i, DBufm*diam*diam*vrat[i] {bufm cabufm}

    : cell membrane ca pump
    ~ ca[0] <-> sump  ((0.001)*parea*gamma*u(ca[0]/(1 (mM)), cath/(1 (mM))), (0.001)*parea*gamma*u(ca[0]/(1 (mM)), cath/(1 (mM))))
    ica_pmp = 2*FARADAY*(f_flux - b_flux)/parea

	: dynamics of IP3 ions  
    
	K_gamma = K_R * (1 + (K_p / K_R) * ca[0] / (ca[0] + K_pi))
	v_3K = v_bar_3K * ca[0]^4/(ca[0]^4 + K_D^4) * ip3i / (ip3i + K_3)
	v_delta = v_bar_delta/(1 + ip3i/kappa_delta)* ca[0]^2 / (ca[0]^2 + K_PLCdelta^2)            
	: v_glu = v_bar_beta * modelStim^0.7 / (modelStim^0.7 + K_gamma^0.7)
	v_glu = v_bar_beta * modelStim / (modelStim + K_gamma)
	  ~ ip3i << ((PI*diam*diam*(v_glu + v_delta - v_3K - r_bar_5P * ip3i))/2)
	: ~ ip3i << (Currentip3*PI*diam*(1e4)/(2*FARADAY))
	
	
    : all currents except cell membrane ca pump
    ~ ca[0] << (-(ica - ica_pmp_last)*PI*diam/(2*FARADAY))  : ica is Ca efflux
    : radial diffusion
    FROM i=0 TO Nannuli-2 {
		
        ~ ca[i] <-> ca[i+1]  (DCa*frat[i+1], DCa*frat[i+1])
        ~ bufm[i] <-> bufm[i+1]  (DBufm*frat[i+1], DBufm*frat[i+1])
		
    }
	
    : buffering
    dsq = diam*diam
    FROM i=0 TO Nannuli-1 {
        dsqvol = dsq*vrat[i]
        ~ ca[i] + bufs[i] <-> cabufs[i]  (kfs*dsqvol, (0.001)*KDs*kfs*dsqvol)
        ~ ca[i] + bufm[i] <-> cabufm[i]  (kfm*dsqvol, (0.001)*KDm*kfm*dsqvol)
    }
    : SERCA pump, channel, and leak
    FROM i=0 TO Nannuli-1 {
        dsqvol = dsq*vrat[i]
        : pump
        ~ ca[i] << (-dsqvol*alpha*vmax*ca[i]^2 / (ca[i]^2 + Kp^2))
        : channel
        ~ hc[i] <-> ho[i]  (kon*Kinh, kon*ca[i])
        ~ ca[i] << ( dsqvol*alpha*jmax*(1-(ca[i]/caer)) * ( (ip3i/(ip3i+Kip3)) * (ca[i]/(ca[i]+Kact)) * ho[i] )^3 )
        : leak
        ~ ca[i] << (dsqvol*alpha*L[i]*(1 - (ca[i]/caer)))
    }
	
    cai = ca[0]
    fluo = cabufm[0]
    fluoNew = (BufferAlpha * cabufm[0] + ca[0] - BufferAlpha*(TBufm - bufm_0) - cai0)/(BufferAlpha*(TBufm - bufm_0) + cai0)
}

FUNCTION u(x, th) {
    if (x>th) {
        u = 1
    } else {
        u = 0
    }
}