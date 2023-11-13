COMMENT
        calcium accumulation into a volume of area*depth next to the
        membrane with a decay (time constant tau) to resting level
        given by the global calcium variable cai0_ca_ion
ENDCOMMENT

NEURON {
        SUFFIX gabaacum
        USEION gaba READ gabao WRITE gabao
        RANGE depth, tau, gabao0
}

UNITS {
        (mM) = (milli/liter)
        (mA) = (milliamp)
        F = (faraday) (coulombs)
}

PARAMETER {
        depth = 1 (nm)  : assume volume = area*depth
        tau = 10 (ms)
        gabao0 = 50e-6 (mM)       : Requires explicit use in INITIAL
                        : block for it to take precedence over gabao0_gaba_ion
                        : Do not forget to initialize in hoc if different
                        : from this default.
}

ASSIGNED {
        igaba (mA/cm2)
}

STATE {
        gabao (mM)
}

INITIAL {
        gabao = gabao0
}

BREAKPOINT {
        SOLVE integrate METHOD derivimplicit
}

DERIVATIVE integrate {
        gabao' = -igaba/depth/F/2 * (1e7) + (gabao0 - gabao)/tau
}