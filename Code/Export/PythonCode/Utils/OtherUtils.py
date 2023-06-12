
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
    
def codeContractViolation():
    raise Exception('Bug in Exporter: Code contract violation')
    