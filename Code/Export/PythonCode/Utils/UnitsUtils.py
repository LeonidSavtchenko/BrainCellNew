
from neuron import h
from Utils.OtherUtils import hocObj


class UnitsUtils:
    
    def getUnitsCommentForExposedOrSweptVar(var):
        comment = h.ref('')
        var.getUnitsCommentOrEmpty(comment)
        return comment[0]
        
    def getUnitsForWatchedVar(customExpr):
        
        # The next command gives errors like "Cannot find the symbol for  dendA1_00.PcalBar_CAl( 0.05 )"
        #   return h.units(customExpr)
        
        # !!!! test this for PPs
        units = h.ref('')
        h.getWatchedVarUnits(customExpr, units)
        return units[0]
        
    def getUnitsForDmOrSynPart(isDmOrSynPart, compIdx, mechIdx, varName, varNameWithIndex):
        enumDmPpNc = hocObj.compUtils.getComp(isDmOrSynPart, compIdx).enumDmPpNc
        units = h.ref('')
        hocObj.mth.getVarUnits(enumDmPpNc, mechIdx, varName, varNameWithIndex, units)
        return units[0]
        