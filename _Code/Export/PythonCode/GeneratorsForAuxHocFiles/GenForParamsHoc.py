
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
            unitsCommentOrEmpty = UnitsUtils.getUnitsCommentOrEmptyForExposedOrSweptVar1(exposedVar)
            lines.append(f'// {exposedVar.s}{unitsCommentOrEmpty}')
            value = exposedVar.getValue()
            if exposedVar.isInteger:
                value = int(value)
            lines.append(f'{getExposedVarName(concExposedVarIdx)} = {value}')
            
        return lines
        