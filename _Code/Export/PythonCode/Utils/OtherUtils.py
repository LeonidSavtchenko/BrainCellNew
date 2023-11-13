
import os, re
from OtherInterModularUtils import *


indentSize = 4
stdIndent = ' ' * indentSize


def getAllSectionNamesExceptNanogeometry():
    # Get all names (base geometry, nanogeometry, etc.)
    # !! it's not optimal because:
    # (1) there is a lot of nanogeometry sections with known names (no need to use slow "forall")
    # (2) we already had all base geometry names at some point before (in Import module)
    allSecNames = hocObj.getAllSectionNames()
    
    if len(allSecNames) == 0:
        codeContractViolation()
        
    for secName in allSecNames:
        if isNanoGeometrySection(secName.s):
            continue
        yield secName
        
def getAllLinesFromFile(relFilePathName):
    absFilePathName = os.getcwd() + '\\' + relFilePathName
    with open(absFilePathName, 'r') as inFile:
        inText = inFile.read()
    return inText.strip().splitlines()  # All newline characters are removed here
    
def exportTheseTemplatesFromThisDir(lines, relDirPath, templNames):
    isFirstTemplate = True
    for templName in templNames:
        if not isFirstTemplate:
            lines.append('')
        relFilePathName = relDirPath + '\\' + templName + '.hoc'
        newLines = getAllLinesFromFile(relFilePathName)
        lines.extend(newLines)
        lines.append('')
        isFirstTemplate = False
        
def prepareUniqueNameId(name):
    if name == '' or name[0] == ' ' or name[-1] == ' ' or '  ' in name:
        # Keep in sync with hoc:chooseUniqueNameForCompartmentForMechManager
        codeContractViolation()
    # !!! BUG: multiple different names are mapped to the same ID, e.g. "A1", "A 1", "A (1)" etc.
    # !!! compile the expression once with re.compile and then reuse for better performance
    return re.sub(r'[^0-9A-Za-z_]', '', name)
    
def getExposedVarName(exposedVarIdx):
    return f'EXPOSED_VAR_{exposedVarIdx + 1}'
    
def getSweptVarName(sweptVarIdx):
    return f'SWEPT_VAR_{sweptVarIdx + 1}'
    
def emptyParagraphHint():
    return '// (Empty paragraph)'
    
def getIndent(line):
    for idx, char in enumerate(line):
        if not char.isspace():
            return ' ' * idx
    codeContractViolation()
    