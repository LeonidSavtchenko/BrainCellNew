
from neuron import h
from OtherInterModularUtils import hocObj


def splitSectionsIntoGroupsBasedOnMechInsertion(list_ref):
    
    mth = hocObj.mth
    
    numMechs = int(mth.getNumMechs(0))
    
    mechName = h.ref('')
    
    arrayOfFlagsToSecListDict = {}
    
    for sec_ref in list_ref:
        arrayOfFlags = [False] * numMechs
        for mechIdx in range(numMechs):
            mth.getMechName(0, mechIdx, mechName)
            if h.ismembrane(mechName, sec=sec_ref.sec):
                arrayOfFlags[mechIdx] = True
        tupleOfFlags = tuple(arrayOfFlags)  # Just so we can use it as a dict key
        try:
            thisList_ref = arrayOfFlagsToSecListDict[tupleOfFlags]
        except KeyError:
            thisList_ref = h.List()
            arrayOfFlagsToSecListDict[tupleOfFlags] = thisList_ref
        thisList_ref.append(sec_ref)
        
    listOfList_ref = h.List()
    for thisList_ref in arrayOfFlagsToSecListDict.values():
        listOfList_ref.append(thisList_ref)
        
    # !!! think about ordering the output groups based on "distance" within each group (e.g. min or average)
    return listOfList_ref
    