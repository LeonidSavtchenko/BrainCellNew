
from neuron import h
from OtherInterModularUtils import hocObj


class BiophysJsonExportImportUtils:
    
    varTypeNames = ['PARAMETER', 'ASSIGNED', 'STATE']
    
    
    @classmethod
    def showVerbatimModelWarning(cls, compIdx, mechIdx, varType, varIdx, arrayIndex):
        
        compIdx = int(compIdx)
        comp = hocObj.mmAllComps[compIdx]
        (mechName, varTypeName, varNameWithIndex) = cls.getNamesForMsg(compIdx, mechIdx, varType, varIdx, arrayIndex)
        
        h.continue_dialog(f'Warning: Import of "Verbatim data" inhom model for "{mechName} \ {varTypeName} \ {varNameWithIndex}" in "{comp.name}" requires that the recipient cell has exactly the same total number of segments in this compartment.')
        # !!! strictly speaking, the same number of segments doesn't mean the same diam and L,
        #     so even successfully imported VerbatimDistFuncHelper for g_pas in LargeGlia won't necessarily match diam and L in the recipient cell
        
    # !!!! maybe just reuse recComp, mechName, varTypeIdx, varTypeName, varName and varNameWithIndex obtained upstream
    @classmethod
    def getNamesForMsg(cls, compIdx, mechIdx, varType, varIdx, arrayIndex):
        
        mth = hocObj.mth
        
        comp = hocObj.mmAllComps[compIdx]
        mechName = h.ref('')
        mth.getMechName(0, mechIdx, mechName)
        varTypeIdx = int(mth.convertVarTypeToVarTypeIdx(varType))
        varTypeName = cls.varTypeNames[varTypeIdx]      # !!!! maybe just call mth.getVarTypeName
        varName = h.ref('')
        arraySize = mth.getVarNameAndArraySize(0, mechIdx, varType, varIdx, varName)
        varNameWithIndex = h.ref('')
        mth.getVarNameWithIndex(varName, arraySize, arrayIndex, varNameWithIndex)
        
        return (mechName[0], varTypeName, varNameWithIndex[0])
        