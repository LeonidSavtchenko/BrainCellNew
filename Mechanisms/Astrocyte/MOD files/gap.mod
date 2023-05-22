: Voltage gap junstion
NEURON {
    POINT_PROCESS Gap
    NONSPECIFIC_CURRENT i
    RANGE r, i, VoltageGap
    POINTER vgap
}

PARAMETER {
    r = 100000(megohm)
    VoltageGap = -85 (millivolt)
}

ASSIGNED {
    v (millivolt)
    vgap (millivolt)
    i (nanoamp)
}

BREAKPOINT {
    i = (-VoltageGap +vgap)/r
}