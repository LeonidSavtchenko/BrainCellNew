
COMMENT
    Extracellular Diffusion Calculation and Consumption Helper (membrane mechanism)
    
    This membrane mechanism plays the next roles: ... !!!!
    
    In case you want to add new species (or delete old ones), look for the lines below marked as "### Edit here when changing the species list ###".
    Any changes to the lines must be done synchronously with the changes to the HOC files "SpeciesLibrary.hoc" and "ExtracellularListItems.hoc".
ENDCOMMENT

: !!! think about moving this file to a common folder for both Astrocyte and Neuron, compile separately, and load individually with nrn_load_dll

: !!! need to hide this mechanism in our Manager of Biophysics

: !!! when variable time step is used, it's important to schedule calls of our code in this MOD file on each "on-off" event and each "spike" event of each extracellular source

NEURON {
    SUFFIX ECDCalcAndConsHelper
    
    : !!! investigate whether enlisting all available ions here causes significant performance or memory penalties compared to the case when we enlist only the used ones
    :     if it does, then consider creation of individual MOD file for each ion OR generation of this single MOD file from Python, then compile it and load dynamically
    : !!! do I need to add READ and VALENCE as well?
    :     UPD: maybe no need to add READ because we already WRITE, so an attempt to use the read value like "oinit"
    :          would lead to cumulative effect of summation
    : !!! ### Edit here when changing the species list ###
    USEION na WRITE nao
    USEION k WRITE ko
    USEION ca WRITE cao
    USEION frapion WRITE frapiono
    USEION ip3 WRITE ip3o
    
    : !!! this compiles fine, but causes hanging when we launch a HOC file
    : USEION abcxyz WRITE abcxyzo
    
    : !!! it would be better to pass them with POINTER to array
    : !!! ### Edit here when changing the species list ###
    GLOBAL naoinit, koinit, caoinit, frapionoinit, ip3oinit
    
    : !!! compiler warning here: Use of POINTER is not thread safe
    : !!! try to make ptr_ecSrcLibDataVec a GLOBAL POINTER or POINTER GLOBAL. UPD: compiler error
    : !!! try to reuse a simple GLOBAL variable (of type double or double[]) as a POINTER
    
    : The pointer to an object of type "struct SpeciesLibrary"
    POINTER ptr_spcLibDataVec
    
    : The pointer to an object of type "struct ExtracellularSourcesLibrary"
    POINTER ptr_ecSrcLibDataVec
    
    : The pointer to a matrix row (effectively a vector) such that given extracellular source index "ecsIdx",
    : the value "ptr_segm3DSpecificDataMatRow[ecsIdx]" has different meaning depending on the source shape:
    :   * "point" - distance from the 3D point to the segment centre
    :   * "ball"  - 0/1 flag indicating whether the segment centre is inside the ball
    POINTER ptr_segm3DSpecificDataMatRow
    
    POINTER ptr_numImpsSoFarDataVec
    
    : !!! maybe combine these two into a special template/struct
    GLOBAL maxNumImpsPerECS
    POINTER ptr_impTimesDataMatrix
}

UNITS {
    PI = (pi) (1)
}

PARAMETER {
    : !!! can I read the values directly from GLOBAL vars? UPD: try to declare them as EXTERNAL or BBCOREPOINTER:
    :     https://nrn.readthedocs.io/en/latest/python/modelspec/programmatic/mechanisms/nmodl2.html
    :     having pointers to GLOBAL-s would be a better solution because it allows user to change a GLOBAL variable
    :     during the simulation on the fly and immediately have the effect in this MOD file
    : !!! otherwise, maybe set all to -1 by default
    : !!! it would be better to pass them with POINTER to array
    : !!! ### Edit here when changing the species list ###
    naoinit = 140 (mM)      : na_ion\GLOBAL\nao0_na_ion
    koinit = 2.5 (mM)       : k_ion\GLOBAL\ko0_k_ion
    caoinit = 2 (mM)        : ca_ion\GLOBAL\cao0_ca_ion
    frapionoinit = 1 (mM)   : frapion_ion\GLOBAL\frapiono0_frapion_ion
    ip3oinit = 1 (mM)       : ip3_ion\GLOBAL\ip3o0_ip3_ion
    
    ptr_spcLibDataVec
    ptr_ecSrcLibDataVec
    
    ptr_segm3DSpecificDataMatRow
    
    ptr_numImpsSoFarDataVec
    
    maxNumImpsPerECS = -1
    ptr_impTimesDataMatrix
}

ASSIGNED {
    : !!! ### Edit here when changing the species list ###
    nao (mM)
    ko (mM)
    cao (mM)
    frapiono (mM)
    ip3o (mM)
    
    : !!! this compiles fine, but causes hanging when I launch a HOC file
    : abcxyzo (mM)
}

: !!! compiler warning here: VERBATIM blocks are not thread safe
VERBATIM
    // !!! ### Edit here when changing the species list ###
    #define numSpeciesInMOD 5
    
    struct SpeciesInfo {
        double diff;
    };
    
    struct SpeciesLibrary {
        double numSpeciesInHOC;
        struct SpeciesInfo speciesInfo[0];  // !!! keep this one last not to specify the actual array size
    };
    
    struct ECSSpatialInfo {
        double enumPointBall;
        double x;               // !!! no need to pass x, y, z into MOD file
        double y;               //
        double z;               //
        double radiusOrMinus1;  // !!! maybe no need to pass this as well (and merge with ECSCapacityInfo.pointCapacityRadiusOrMinus1)
    };
    
    struct ECSTemporalInfo {
        double enumStaticSwitchSpike;
        double startTimeOrMinus1;
        double endTimeOrMinus1;
        double spikeTimeOrMinus1;
        // double durationOrMinus1;           // !!!!
        double isSeriesOrMinus1;
    };
    
    struct ECSCapacityInfo {
        double ssOrMinus1;
        double pointCapacityRadiusOrMinus1;     // !!! maybe merge this with ECSSpatialInfo.radiusOrMinus1
        double numMoleculesOrMinus1;
        double delta_oOrMinus1;
    };
    
    /* !!!!
    struct ECSSeriesInfo {
        double *ptr_vec_numImpsSoFar;
        double *impTimes;
    };
    */
    
    struct ExtracellularSource {
        double speciesIdx;
        struct ECSSpatialInfo spatialInfo;
        struct ECSTemporalInfo temporalInfo;
        struct ECSCapacityInfo capacityInfo;
        // !!!! struct ECSSeriesInfo seriesInfo;        // !!!! don't add it here because we pass the array of ExtracellularSource-s from HOC
    };
    
    struct ExtracellularSourcesLibrary {
        double numECSs;
        struct ExtracellularSource ecs[0];  // !!! keep this one last not to specify the actual array size
    };
    
    struct SpeciesLibrary *ptr_spcLib;
    struct ExtracellularSourcesLibrary *ptr_ecSrcLib;
    
    
    double *ptr_vec_segm3DSpecificData;
    
    // !!! ideally, we need to hide these two into "struct ECSSeriesInfo" being a part of "struct ExtracellularSource"
    double *ptr_vec_numImpsSoFar;
    double *ptr_mat_impTimes;
    
    // !!!! do not convert maxNumImpsPerECS to int each time
    #define IMPULSE_TIME(ecsIdx, impIdx) (ptr_mat_impTimes[(ecsIdx) * (int)maxNumImpsPerECS + (impIdx)])
    
    double *ptr_vec_o[numSpeciesInMOD];
    
    // !!! will be defined below the first call (just for convenience)
    void updateOutConcGivenECSAndImp(int ecsIdx, int impIdxOrMinus1);
    
    void codeContractViolation() {
        execerror("\n\n    Bug in BrainCell program: Code contract violation", "\n    Please report this problem to the developer along with the call stack shown below\n");
    }
ENDVERBATIM

INITIAL {
    checkPointers()
    assignPointers()    : !!! maybe merge into one
    calcAllOutConcs()   :
}

BREAKPOINT {
    assignPointers()
    calcAllOutConcs()
}

PROCEDURE checkPointers() {
    VERBATIM
        if (&ptr_spcLibDataVec == NULL ||
            &ptr_ecSrcLibDataVec == NULL ||
            &ptr_segm3DSpecificDataMatRow == NULL ||
            &ptr_numImpsSoFarDataVec == NULL ||
            maxNumImpsPerECS == -1 ||
            &ptr_impTimesDataMatrix == NULL) {
            
            // This membrane mechanism was inserted, but its params were not initialized
            codeContractViolation();
        }
        // !!! maybe loop through all used "*OrMinus1" vars and make sure they don't equal -1 (use codeContractViolation)
    ENDVERBATIM
}

PROCEDURE assignPointers() {
    
    VERBATIM
        // !!! why do I need to assign the next 6 pointers on each breakpoint?
        //     (they behave like shared between the segments - need to look into C code)
        //     UPD 1: VERBATIM block is not allowed inside NEURON, PARAMETER or ASSIGNED,
        //            so cannot move the declarations of the pointers there
        //     UPD 2: if I declare 2 vars with the same name in different MOD files, compiler gives an error
        
        // !!! maybe I can call some HOC code here to do this in order to be more flexible with regard to adding/deleting species
        // !!! ### Edit here when changing the species list ###
        ptr_vec_o[0] = &nao;
        ptr_vec_o[1] = &ko;
        ptr_vec_o[2] = &cao;
        ptr_vec_o[3] = &frapiono;
        ptr_vec_o[4] = &ip3o;
        
        
        // ptr_b = (void*)&ptr_a;   // !!! would work fine below as well (but won't work after migration from C to C++)
        
        ptr_spcLib = (struct SpeciesLibrary*)&ptr_spcLibDataVec;
        ptr_ecSrcLib = (struct ExtracellularSourcesLibrary*)&ptr_ecSrcLibDataVec;
        ptr_vec_segm3DSpecificData = (double*)&ptr_segm3DSpecificDataMatRow;
        
        ptr_vec_numImpsSoFar = (double*)&ptr_numImpsSoFarDataVec;
        ptr_mat_impTimes = (double*)&ptr_impTimesDataMatrix;
        
        /* !!!! is there a better way to pass the pointers directly into the structs?
        for (int ecsIdx = 0; ecsIdx < (int)ptr_ecSrcLib->numECSs; ecsIdx++) {
            struct ECSSeriesInfo *seriesInfo = &ptr_ecSrcLib->ecs[ecsIdx].seriesInfo;
            seriesInfo->ptr_vec_numImpsSoFar = &((double*)&ptr_numImpsSoFarDataVec)[ecsIdx];
            
            // !!!! when NEURON will resize the Vector, this pointer won't be correct anymore
            
            seriesInfo->impTimes = &((double*)&ptr_impTimesDataMatrix)[(int)maxNumImpsPerECS * ecsIdx];
            
            // !!!! do not convert maxNumImpsPerECS from double to int on each iteration
        }
        */
        
        // Make sure HOC and MOD code is synced with regard to the species list
        if (ptr_spcLib->numSpeciesInHOC != numSpeciesInMOD) {
            codeContractViolation();
        }
    ENDVERBATIM
    
}

PROCEDURE calcAllOutConcs() {
    
    VERBATIM
        
        
        // !!!!
        static double last_printed_t = -1;
        if (t != last_printed_t) {
            printf("MM-BREAKPOINT: t=%g\n", t);
            last_printed_t = t;
        }
        
        
        
        // !!! maybe I can call some HOC code here to do this in order to be more flexible with regard to adding/deleting species
        // !!! maybe do not modify the species for which we don't have any sources
        // !!! it would be better to pass all "*oinit" with POINTER to array and use a cycle here
        // !!! ### Edit here when changing the species list ###
        *ptr_vec_o[0] = naoinit;
        *ptr_vec_o[1] = koinit;
        *ptr_vec_o[2] = caoinit;
        *ptr_vec_o[3] = frapionoinit;
        *ptr_vec_o[4] = ip3oinit;
        
        for (int ecsIdx = 0; ecsIdx < (int)ptr_ecSrcLib->numECSs; ecsIdx++) {
            
            struct ExtracellularSource *ptr_ecSrc = &ptr_ecSrcLib->ecs[ecsIdx];
            
            if (ptr_ecSrc->temporalInfo.isSeriesOrMinus1 != 1.0) {
                updateOutConcGivenECSAndImp(ecsIdx, -1);
            } else {
                int numImpsSoFar = (int)ptr_vec_numImpsSoFar[ecsIdx];
                for (int impIdx = 0; impIdx < numImpsSoFar; impIdx++) {
                    updateOutConcGivenECSAndImp(ecsIdx, impIdx);
                }
            }
        }
    ENDVERBATIM
    
}

VERBATIM

    void updateOutConcGivenECSAndImp(int ecsIdx, int impIdxOrMinus1) {
        
        struct ExtracellularSource *ptr_ecSrc = &ptr_ecSrcLib->ecs[ecsIdx];
        
        int spcIdx = ptr_ecSrc->speciesIdx;
        
        switch ((int)ptr_ecSrc->spatialInfo.enumPointBall) {
            case 0:     // "point" shape
                
                // Distance from the 3D point to the segment centre
                double distance = ptr_vec_segm3DSpecificData[ecsIdx];
                
                switch ((int)ptr_ecSrc->temporalInfo.enumStaticSwitchSpike) {
                    case 0:     // "static" dynamics
                        // !!! I can pass one product var instead of two factor vars into this MOD file
                        *ptr_vec_o[spcIdx] += ptr_ecSrc->capacityInfo.ssOrMinus1 * ptr_ecSrc->capacityInfo.pointCapacityRadiusOrMinus1 / distance;
                        
                        break;
                    case 2:         // "spike" dynamics
                        double delta_t;
                        if (impIdxOrMinus1 == -1) {
                            delta_t = t - ptr_ecSrc->temporalInfo.spikeTimeOrMinus1;
                        } else {
                            delta_t = t - IMPULSE_TIME(ecsIdx, impIdxOrMinus1);
                        }
                        
                        if (delta_t < 0) {
                            break;
                        }
                        
                        // !!! optimize the equation:
                        // -pow(Distance, 2.0) / (4.0 * Diff) -> use Distance*Distance and cache before 1st iteration
                        
                        double prod = 4.0 * ptr_spcLib->speciesInfo[spcIdx].diff * delta_t;
                        double delta_o = ptr_ecSrc->capacityInfo.numMoleculesOrMinus1 / pow(PI * prod, 1.5) * exp(-pow(distance, 2.0) / prod);
                        
                        *ptr_vec_o[spcIdx] += delta_o;
                        
                        break;
                    default:
                        codeContractViolation();
                }
                
                break;
            case 1:         // "ball" shape
                
                // 0/1 flag indicating whether the segment centre is inside the ball
                double isInsideBall = ptr_vec_segm3DSpecificData[ecsIdx];
                
                if (!isInsideBall) {
                    break;
                }
                
                // !!! no "bool" in this C by default, and cannot #include <stdbool.h>
                int isOnOrOff;
                
                switch ((int)ptr_ecSrc->temporalInfo.enumStaticSwitchSpike) {
                    case 0:     // "static" dynamics
                        isOnOrOff = 1;
                        
                        break;
                    case 1:     // "switch" dynamics
                    
                        // !!! this won't work well, especially for variable time step method
                        //     the best solution would be to schedule 2 "edge" iterations
                        //     alternatively, for fixed dt, we can show a warning to user when they specify the interval shorter than dt
                        
                        double startTime, endTime;
                        if (impIdxOrMinus1 == -1) {
                            startTime = ptr_ecSrc->temporalInfo.startTimeOrMinus1;
                            endTime = ptr_ecSrc->temporalInfo.endTimeOrMinus1;
                        } else {
                            startTime = IMPULSE_TIME(ecsIdx, impIdxOrMinus1);
                            
                            // !!!! just a temp solution
                            endTime = startTime + (ptr_ecSrc->temporalInfo.endTimeOrMinus1 - ptr_ecSrc->temporalInfo.startTimeOrMinus1);
                            
                            // !!!! must be:
                            // endTime = startTime + ptr_ecSrc->temporalInfo.durationOrMinus1;
                        }
                        isOnOrOff = (t >= startTime && t < endTime);
                        
                        break;
                    case 2:     // "spike" dynamics
                    
                        // !!! this won't work neither for fixed time step, not for variable time step method
                        //     the best solution would be to schedule an "edge" iteration
                        //     alternatively, for fixed dt, we can show a warning to user when they specify the spike time not being a multiple of dt
                        
                        // !!! isOnOrOff = (t == ptr_ecSrc->temporalInfo.spikeTimeOrMinus1);
                        
                        // !!!! do not use "dt" if CVode is enabled
                        
                        // !!!! just a temp solution
                        double spikeTime;
                        if (impIdxOrMinus1 == -1) {
                            spikeTime = ptr_ecSrc->temporalInfo.spikeTimeOrMinus1;
                            isOnOrOff = (t >= spikeTime - dt/2 && t < spikeTime + dt/2);    // !!!! inconsistent
                        } else {
                            spikeTime = IMPULSE_TIME(ecsIdx, impIdxOrMinus1);
                            isOnOrOff = (t > spikeTime - dt && t <= spikeTime + dt);        // !!!!
                        }
                        
                        break;
                    default:
                        codeContractViolation();
                }
                
                if (isOnOrOff) {
                    *ptr_vec_o[spcIdx] += ptr_ecSrc->capacityInfo.delta_oOrMinus1;
                }
                
                break;
            default:
                codeContractViolation();
        }
    
    }

ENDVERBATIM
