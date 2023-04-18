
COMMENT
    This artificial cell plays 2 roles:
    1. It implements the release probability mechanics.
    2. It informs HOC code about synaptic events.
    
    To use it, we replace this chain:
        NetCon -> Target PP
    with longer one:
        NetCon -> SynEventsFilterWatcher -> NetCon -> Target PP
    (The second NetCon must have zero delay and the same weight as the first one.)
    
    Warning: The implementation is not thread-safe.
             (Otherwise we would have to use a different RNG for each instance of SynEventsFilterWatcher.)
    
    Note: To use RNG of much higher (cryptographic) quality, which is perhaps 4 times slower, execute the next command in HOC:
              use_mcell_ran4(1)
          (However, this will have a global effect for NEURON environment.)
ENDCOMMENT

NEURON {
    ARTIFICIAL_CELL SynEventsFilterWatcher
    RANGE release_probability, isAnyEventsOnThisIter
}

PARAMETER {
    : The probability in Bernoulli distribution
    : 0 - reject all incoming events, 1 - pass all events downstream
    release_probability = -1    <0, 1>
}

ASSIGNED {
    : On each synaptic event, this flag will be set to 1 from this MOD file;
    : on each iteration, it will be read and set back to 0 from HOC code
    isAnyEventsOnThisIter
    
    : This flag is private to the MOD file (i.e. not exposed in UI)
    isRPeq1
}

: It's enough to set the seed only once per rank (i.e. for just one instance of SynEventsFilterWatcher)
PROCEDURE setSeed(x) {
    : "set_seed" takes an argument of type "double"
    set_seed(x)
}

INITIAL {
    isAnyEventsOnThisIter = 0
    isRPeq1 = (release_probability == 1)
}

NET_RECEIVE (w) {
    : When the first operand of "||" is 1, the second one is not evaluated (in contrast to HOC language)
    if (isRPeq1 || scop_random() < release_probability) {
        net_event(t)
        isAnyEventsOnThisIter = 1
    }
}
