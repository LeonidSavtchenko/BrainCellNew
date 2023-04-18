
COMMENT
    This artificial cell implements the release probability mechanics.
    To use it, we replace this chain:
        NetCon -> Target PP
    with longer one:
        NetCon -> PostNetConEventFilter -> NetCon -> Target PP
    (The second NetCon must have zero delay and the same weight as the first one.)
    
    Warning: The implementation is not thread-safe.
             (Otherwise we would have to use a different RNG for each instance of PostNetConEventFilter.)
    
    Note: To use RNG of much higher (cryptographic) quality, which is perhaps 4 times slower, execute the next command in HOC:
              use_mcell_ran4(1)
          (However, this will have a global effect for NEURON environment.)
ENDCOMMENT

NEURON {
    ARTIFICIAL_CELL PostNetConEventFilter
    RANGE release_probability, isAnyEventsOnThisIter
}

PARAMETER {
    : The probability in Bernoulli distribution
    : 0 - reject all incoming events, 1 - pass all events downstream
    : (in HOC code, we prefer not to create PostNetConEventFilter instances with release_probability == 1)
    release_probability = -1    <0, 1>
}

ASSIGNED {
    : On each synaptic event, this flag will be set to 1 from this MOD file;
    : on each iteration, it will be read and set back to 0 from HOC code
    isAnyEventsOnThisIter
}

: It's enough to set the seed only once per rank (i.e. for just one instance of PostNetConEventFilter)
PROCEDURE setSeed(x) {
    : "set_seed" takes an argument of type "double"
    set_seed(x)
}

INITIAL {
    isAnyEventsOnThisIter = 0
}

NET_RECEIVE (w) {
    : In rare case when release_probability == 1, the operator "<=" would be more correct than "<"
    if (scop_random() < release_probability) {
        net_event(t)
        isAnyEventsOnThisIter = 1
    }
}
