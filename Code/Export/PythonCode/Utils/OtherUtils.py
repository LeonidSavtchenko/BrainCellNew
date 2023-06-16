
import os
from neuron import hoc


hocObj = hoc.HocObject()

indentSize = 4
stdIndent = ' ' * indentSize


def getAllLinesFromFile(relFilePathName):
    absFilePathName = os.getcwd() + '\\' + relFilePathName
    with open(absFilePathName, 'r') as inFile:
        inText = inFile.read()
    return inText.strip().splitlines()  # All newline characters are removed here
    
def prepareUniqueNameId(name):
    if name == '' or name[0] == ' ' or name[-1] == ' ' or '  ' in name:
        # Keep in sync with hoc:chooseUniqueNameForCompartmentForMechManager
        codeContractViolation()
    # !! BUG: Two different names "A1" and "A 1" will have the same ID
    return name.replace(' ', '')
    
def getTemplateName(hocTemplInst):
    templName = str(hocTemplInst)
    idx = templName.index('[')
    templName = templName[: idx]
    return templName
    
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
    
def codeContractViolation():
    raise Exception('Bug in Exporter: Code contract violation')
    