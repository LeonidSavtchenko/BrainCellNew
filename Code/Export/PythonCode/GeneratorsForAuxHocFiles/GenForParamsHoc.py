
from Utils.UnitsUtils import UnitsUtils
from Utils.OtherUtils import hocObj, getExposedVarName


class GenForParamsHoc:
    
    # Data members that will be added in the ctor:
    #   _exportOptions
    
    def __init__(self):
        self._exportOptions = hocObj.exportOptions
        
    def getParamsCode(self):
        lines = []
        
        isAnyExposedVars = self._exportOptions.isAnyExposedVars()
        
        if isAnyExposedVars:
            exposedVarsList = self._exportOptions.exposedVarsList
            for exposedVarIdx in range(len(exposedVarsList)):
                lines.append('')
                exposedVar = exposedVarsList[exposedVarIdx]
                lines.append(f'// {exposedVar.s}{UnitsUtils.getUnitsCommentForExposedOrSweptVar(exposedVar)}')
                lines.append(f'{getExposedVarName(exposedVarIdx)} = {exposedVar.getValue()}')
                
        return lines
        