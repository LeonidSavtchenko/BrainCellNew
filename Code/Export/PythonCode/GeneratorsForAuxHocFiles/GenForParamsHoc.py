
from Utils.UnitsUtils import UnitsUtils
from Utils.OtherUtils import hocObj, getExposedVarName


class GenForParamsHoc:
    
    # Keep in sync with GeneratorsForMainHocFile.getParams
    def getParamsCode(self):
        lines = []
        
        concExposedVarsList = list(hocObj.exportOptions.stdExposedVarsList) + list(hocObj.exportOptions.exposedVarsList)
        for concExposedVarIdx in range(len(concExposedVarsList)):
            lines.append('')
            exposedVar = concExposedVarsList[concExposedVarIdx]
            lines.append(f'// {exposedVar.s}{UnitsUtils.getUnitsCommentForExposedOrSweptVar(exposedVar)}')
            lines.append(f'{getExposedVarName(concExposedVarIdx)} = {exposedVar.getValue()}')
            
        return lines
        