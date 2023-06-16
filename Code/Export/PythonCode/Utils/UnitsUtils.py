
from neuron import h
from Utils.OtherUtils import hocObj


class UnitsUtils:
    
    def getUnitsCommentForExposedOrSweptVar(var):
        if var.enumSpDmCeSt < 2:
            isDmOrSynPart = var.enumSpDmCeSt
            units = UnitsUtils.getUnitsForDmOrSynPart(isDmOrSynPart, var.compIdx, var.mechIdx, var.varName, var.varNameWithIndex)
        else:
            units = h.units(var.customExpr)
        if units:
            return f' ({units})'
        else:
            return ''
            
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
        