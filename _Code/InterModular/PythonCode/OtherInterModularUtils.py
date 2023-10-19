
import os
from neuron import h, hoc


hocObj = hoc.HocObject()


def codeContractViolation():
    # !!! we don't pass the message to Exception ctor just because in this case the shown call stack will be split into two parts:
    #     the Python call stack (printed above our text) and the HOC call stack (printed below our text)
    print('\n    Bug in BrainCell program: Code contract violation\n    Please report this problem to the developer along with the call stack shown below\n')
    raise Exception()
    
def getTemplateName(hocTemplInst):
    templName = str(hocTemplInst)
    idx = templName.index('[')
    if idx == -1:
        codeContractViolation()
    templName = templName[: idx]
    return templName
    
def convertPyIterableOfStrsToHocListOfStrObjs(pyIter):
    hocList = h.List()
    for item in pyIter:
        hocList.append(h.String(item))
    return hocList
    
# Called from both Python and HOC
# !!!! fragile logic in the callers of this method:
#      there is no guarantee that user didn't apply, say, liner function to g_pas in LargeGlia and then clicked "Deep rescan" making it verbatim
def isAstrocyteSpecificInhomVar(compIdx, mechIdx, varType, varIdx, arrayIndex):
    
    mth = hocObj.mth
    
    tp = type(compIdx)
    if tp == int or tp == float:
        compName = hocObj.mmAllComps[int(compIdx)].name
    else:
        codeContractViolation()
        
    mechName = h.ref('')
    varName = h.ref('')
    mth.getMechName(0, mechIdx, mechName)
    mth.getVarNameAndArraySize(0, mechIdx, varType, varIdx, varName)
    
    # !!! checking the comp name below is a fragile solution because user could rename the comp;
    #     a better approach would be to have a Boolean flag in each comp (but what to do with it on comp split and merge ops?)
    cond = (hocObj.isAstrocyteOrNeuron and
        compName == 'Large Glia' and
        mechName[0] == 'pas' and
        varType == 1 and    # 1: PARAMETER
        varName[0] == 'g_pas' and
        arrayIndex == 0)
        
    return cond
    
# !!! find a better place for this (not intermodular actually)
def isInPySet(theSet, theItem):
    return theItem in theSet
    
def getDirPath(anyFilePathName):
    return os.path.dirname(anyFilePathName)
    
# !!! not intermodular actually
def getDllFilePathName(anyFilePathName):
    dirPath = getDirPath(anyFilePathName)
    sepChar = anyFilePathName[len(dirPath)]
    return dirPath + sepChar + 'nrnmech.dll'
    