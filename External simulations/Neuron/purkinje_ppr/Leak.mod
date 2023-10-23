TITLE Leak current

COMMENT
From “Low-threshold potassium channels and a low-threshold calcium channel regulate Ca2+ spike firing in the dendrites of cerebellar Purkinje neurons: a modeling study”
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
}
 
NEURON {
        SUFFIX Leak
        NONSPECIFIC_CURRENT il
        RANGE  gl, el
}
 
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
 
PARAMETER {
        v (mV)
        celsius = 37 (degC)
        dt (ms)
        gl = .0003 (mho/cm2)
        el = -68 (mV)
}
  
ASSIGNED {
        il (mA/cm2)
}
 
BREAKPOINT {
:        SOLVE states
        il = gl*(v - el)
}
 
