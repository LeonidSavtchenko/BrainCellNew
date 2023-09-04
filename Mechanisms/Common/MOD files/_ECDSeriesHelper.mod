
COMMENT
    Extracellular Diffusion Series Helper (artificial cell)
    
    This artificial cell plays the next roles: ... !!!!
    !!!! it is used in the chain NetStim -> NetCon -> ECDSeriesHelper
ENDCOMMENT

: !!!! test that code from this MOD file is executed before the code from _ECDCalcAndConsHelper.mod

: !!! think about moving this file to a common folder for both Astrocyte and Neuron, compile separately, and load individually with nrn_load_dll

: !!! need to move this mechanism into "for internal use only" category in our Manager of Synapses

: !!! when variable time step is used (and not only), test that the code from _ECDSeriesHelper.mod and _ECDCalcAndConsHelper.mod is executed immediately on each NetStim spike

NEURON {
    : !!!! why do I have the next warning here and don't have it for SynEventsFilterWatcher.mod?
    :       Notice: ARTIFICIAL_CELL is a synonym for POINT_PROCESS which hints that it
    :       only affects and is affected by discrete events. As such it is not
    :       located in a section and is not associated with an integrator
    :      UPD: check if this warning is related to the problem of the wrong order of calls
    :           (see the comment in NET_RECEIVE)
    ARTIFICIAL_CELL ECDSeriesHelper
    
    : !!! maybe combine these pointers into a special template/struct
    
    POINTER ptr_numImpsSoFarVecElem
    
    : !!!! GLOBAL maxNumImpsPerECS  : !!!! maybe get rid of this (I can use it here just for code contract check)
    POINTER ptr_impTimesDataMatRow
}

PARAMETER {
    ptr_numImpsSoFarVecElem
    
    : !!! maxNumImpsPerECS = -1
    ptr_impTimesDataMatRow
}

: !!! compiler warning here: VERBATIM blocks are not thread safe
VERBATIM
    // !!! ideally, we need to hide this into "struct ECSSeriesInfo" being a part of "struct ExtracellularSource"
    double *ptr_sc_numImpsSoFar;
    double *ptr_vec_impTimes;
ENDVERBATIM

INITIAL {
    assignPointers()
    VERBATIM
        *ptr_sc_numImpsSoFar = 0.0;
    ENDVERBATIM
}

NET_RECEIVE (w) {
    printf("AC-NET_RECEIVE: t=%g\n", t) : //!!!!
    assignPointers()
    VERBATIM
        // !!!! if (numImpsSoFar > maxNumImpsPerECS) then codeContractViolation
        ptr_vec_impTimes[(int)*ptr_sc_numImpsSoFar] = t;
        *ptr_sc_numImpsSoFar += 1.0;
    ENDVERBATIM
    
    : !!!! BUG: for fixed dt, for "ball+spike", when NET_RECEIVE is called on t being multiple of dt,
    :           it is called AFTER the breakpoint in ECDCalcAndConsHelper => this results in missing reaction on this impulse in ECDCalcAndConsHelper
    :           try to connect this AC to some test section (and ideally delete this section) - maybe this will change the order of calls
    
    : MM-BREAKPOINT: t=1.4
    : MM-BREAKPOINT: t=1.5          !!!!
    : AC-NET_RECEIVE: t=1.52726     !!!! bad for me
    : MM-BREAKPOINT: t=1.6
    : MM-BREAKPOINT: t=1.7
    : MM-BREAKPOINT: t=1.8
    : MM-BREAKPOINT: t=1.9          !!!!
    : AC-NET_RECEIVE: t=1.87956     !!!! very bad for me
    : MM-BREAKPOINT: t=2
    :
    : UPD1: when I use PP instead of AC (all inserted into soma), the problem remains
    : UPD2: when I set NetCon.delay = 1, the problem remains
    : IDEA: try to set NetCon.delay = dt and correct the above code as following: "ptr_vec_impTimes[(int)*ptr_sc_numImpsSoFar] = t - dt" (also, shift "start" in NetCon by dt)
    : IDEA (last resort): to use PP instead of AC and insert it into all segments
    
    : !!!! BUG: the membrane mechanism breakpoint is not called for this fractional t (for fixed dt at least),
    :           and "net_event(t)" doesn't help
    
    : !!!! TODO: test vith CVode enabled
}

PROCEDURE assignPointers() {
    VERBATIM
        // !!!! do I need to assign them each time?
        ptr_sc_numImpsSoFar = (double*)&ptr_numImpsSoFarVecElem;
        ptr_vec_impTimes = (double*)&ptr_impTimesDataMatRow;
    ENDVERBATIM
}
