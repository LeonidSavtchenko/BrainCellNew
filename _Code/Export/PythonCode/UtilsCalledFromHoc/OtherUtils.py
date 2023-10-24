
from Utils.OtherUtils import getAllSectionNamesExceptNanogeometry
from OtherInterModularUtils import hocObj


def checkForNotImplementedExportScenario():
    secNames = getAllSectionNamesExceptNanogeometry()
    isNotImpl = any('.' in secName.s for secName in secNames)
    if isNotImpl:
        hocObj.mwh.showNotImplementedWarning('Cannot export the cell because, for the imported base geometry, some section(s) were created inside templates.')
    return isNotImpl
    