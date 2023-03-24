
COMMENT
    This artificial cell implements the release probability mechanism.
    To use it, we replace this chain:
        NetCon -> Target PP
    with longer one:
        NetCon -> PostNetConEventFilter -> NetCon -> Target PP
ENDCOMMENT

: !!?? TITLE PostNetConEventFilter

NEURON {
    : !!?? SUFFIX PostNetConEventFilter
    ARTIFICIAL_CELL PostNetConEventFilter
    RANGE release_probability, isAnyEventsOnThisIter
    : !!?? BBCOREPOINTER
}

PARAMETER {
    : The probability in Bernoulli distribution
    : 0 - reject all incoming events, 1 - pass all events downstream
    : (in HOC code, we prefer not to create such PPs with release_probability == 1)
    release_probability = -1   <0, 1>
}

ASSIGNED {
    isAnyEventsOnThisIter   : This will be read from HOC code on each iteration
}

: !!?? UNITSOFF

: It's enough to set the seed only once per rank (i.e. for just one such PP)
PROCEDURE setSeed(x) {
    : printf("setSeed >> x = %g\n", x)    : !! ok, x is double here
    
    : !! takes double, defined in \nrn-master\src\oc\scoprand.cpp
    set_seed(x)     : !! compiler warns: "set_seed is not thread safe"
    
    : srand(x)      : !! compiler error
}

INITIAL {
    isAnyEventsOnThisIter = 0
    : printf("INITIAL >> release_probability = %g\n", release_probability)      : !! ok
    : printf("INITIAL >> use_mcell_ran4_ = %d\n", use_mcell_ran4_)              : !! compiler error
}

BREAKPOINT {    : !! not sure, maybe use "BEFORE BREAKPOINT" or "AFTER BREAKPOINT" or even "else" block in "NET_RECEIVE"
    : printf("!!BREAKPOINT\n")
    isAnyEventsOnThisIter = 0
}

NET_RECEIVE (w) {
    : printf("NET_RECEIVE >> w = %g, flag = %g\n", w, flag)         : !! compiler error
    LOCAL randomValue
    : !! too coarse-grained generator, RAND_MAX is only 32767
    : !! maybe I can set "use_mcell_ran4_" to 1 to switch to better RNG
    randomValue = scop_random()
    : printf("NET_RECEIVE >> randomValue = %g\n", randomValue)      : !! ok
    if (randomValue < release_probability) {    : In rare case when release_probability == 1, "<=" would be more correct than "<"
        net_event(t)                : !! maybe t +- smth ?
        : net_send(0, 1)  : first arg: time delay; second arg: "0" means external (synaptic) event, "1" means self event
        isAnyEventsOnThisIter = 1
        printf("+\n")
        : !!?? if (flag == 0/1/2/3)
        : !!?? net_send(*, *)
        : !!?? event_time()
        : !!?? net_move(*)
        : !!?? firetime
    } else {
        printf("-\n")
    }
}

: !! "normrand" is defined in \nrn-master\src\scopmath\normrand.c
