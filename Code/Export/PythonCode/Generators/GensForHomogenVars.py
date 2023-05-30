
import math
from neuron import h, hoc
from OtherUtils import *


class GensForHomogenVars:
    
    _hocObj = hoc.HocObject()
    
    # Other data members that will be added in the ctor:
    #   _exportOptions
    
    def __init__(self):
        self._exportOptions = self._hocObj.exportOptions
        
    def initHomogenBiophysics(self):
        if not self._exportOptions.isExportDistMechs:
            return emptyParagraphHint()
            
        lines = []
        
        mmAllComps = self._hocObj.mmAllComps
        
        # Create number of proc-s to prepare and set "isMechInserted" and "mechStds" for each mech comp
        procNames = []
        mth = self._hocObj.mth
        enumDmPpNc = 0
        for comp in mmAllComps:
            procNameId = prepareUniqueNameId(comp.name)
            procName = 'addHomogenBiophysInfoTo{}Comp'.format(procNameId)
            procNames.append(procName)
            lines.append('proc {}() {{ localobj comp, mechStd'.format(procName))
            lines.append('    comp = $o1')
            lines.append('    ')
            numMechs = int(mth.getNumMechs(enumDmPpNc))
            for mechIdx in range(numMechs):
                if comp.isMechInserted[mechIdx]:
                    lines.append('    comp.isMechInserted[{}] = 1'.format(mechIdx))
            lines.append('    ')
            for mechIdx in range(numMechs):
                if not comp.isMechInserted[mechIdx]:
                    continue
                # Generate code to init "mechStds" array slice for this mech of this comp
                newLines = self._exportHomogenVarsOfThisMech(comp, mechIdx, self._exportOptions.isExportDistMechAssignedAndState, self._exportOptions.isExportDistMechInhoms)
                lines.extend(newLines)
                
            lines[-1] = '}'
            lines.append('')
            
        # For each comp, generate the call of corresponding proc
        newLines = self._finishExportOfHomogenVars(mmAllComps, 'mmAllComps', procNames, 'initHomogenBiophysics')
        lines.extend(newLines)
        
        return lines
        
    # Keep in sync with hoc:EnumSynCompIdxs.init, hoc:createOrImportSynComps and py:createReducedSynComps
    def initHomogenSynVars(self):
        if not self._exportOptions.isExportSyns:
            return emptyParagraphHint()
            
        lines = []
        
        synGroup = self._hocObj.synGroup
        
        mechIdxs = [None] * 4
        mechIdxs[0] = int(synGroup.getMechIdxAndOptionalName(0))    # "Source PP"
        mechIdxs[1] = 0                                             # "NetCon"
        mechIdxs[2] = int(synGroup.getMechIdxAndOptionalName(1))    # "Target PP"
        mechIdxs[3] = int(synGroup.getMechIdxAndOptionalName(2))    # "Single PP"
        
        smAllComps = self._hocObj.smAllComps
        
        # Create number of proc-s to prepare and set "mechStds" for each syn comp
        procNames = []
        for compIdx, mechIdx in zip(range(len(smAllComps)), mechIdxs):
            comp = smAllComps[compIdx]
            procNameId = prepareUniqueNameId(comp.name)
            procName = 'addHomogenVarsInfoTo{}SynComp'.format(procNameId)
            procNames.append(procName)
            lines.append('proc {}() {{ localobj comp, mechStd'.format(procName))
            lines.append('    comp = $o1')
            lines.append('    ')
            if self._isExportedSynComp(compIdx):
                newLines = self._exportHomogenVarsOfThisMech(comp, mechIdx, self._exportOptions.isExportSynAssignedAndState, self._exportOptions.isExportSynInhoms)
                lines.extend(newLines)
                
            lines[-1] = '}'
            lines.append('')
            
        # For each comp, generate the call of corresponding proc
        newLines = self._finishExportOfHomogenVars(smAllComps, 'smAllComps', procNames, 'initHomogenVars')
        lines.extend(newLines)
        
        return lines
        
        
    # Generate code to init "mechStds" array slice for this mech of this comp
    def _exportHomogenVarsOfThisMech(self, comp, mechIdx, isExportAssignedAndState, isExportInhoms):
        lines = []
        
        mechName = h.ref('')
        mth = self._hocObj.mth
        enumDmPpNc = comp.enumDmPpNc
        mth.getMechName(enumDmPpNc, mechIdx, mechName)
        mechName = mechName[0]
        if enumDmPpNc != 2:
            if isExportAssignedAndState:
                maxVarType = 3
            else:
                maxVarType = 1
        else:
            maxVarType = 1
            
        for varType in range(1, maxVarType + 1):    # 1: "PARAMETER", 2: "ASSIGNED", 3: "STATE"
            varTypeIdx = int(mth.convertVarTypeToVarTypeIdx(varType))
            varTypeName = h.ref('')
            mth.getVarTypeName(varType, varTypeName)
            varTypeName = varTypeName[0]
            if enumDmPpNc != 2:
                defaultMechStd = h.MechanismStandard(mechName, varType)
            else:
                defaultMechStd = h.FakeMechanismStandardForNetCon()
            newLines = []
            isAllDefault = True
            if enumDmPpNc != 2:
                newLines.append('    mechStd = new MechanismStandard("{}", {})    // {}'.format(mechName, varType, varTypeName))
            else:
                newLines.append('    mechStd = new FakeMechanismStandardForNetCon()')
            numVars = int(mth.getNumMechVars(enumDmPpNc, mechIdx, varType))
            for varIdx in range(numVars):
                varName = h.ref('')
                arraySize = int(mth.getVarNameAndArraySize(enumDmPpNc, mechIdx, varType, varIdx, varName))
                varName = varName[0]
                for arrayIndex in range(arraySize):
                    value = comp.mechStds[mechIdx][varTypeIdx].get(varName, arrayIndex)
                    defaultValue = defaultMechStd.get(varName, arrayIndex)
                    # !! not sure about the 2nd condition in IF below,
                    #    but it found out for ASSIGNED "ko_IKa" from "IPotassium.mod" that its default value
                    #    is different depending on the moment when we created a new MechanismStandard:
                    #    just after the start of our program (defaultValue = 0) or now (defaultValue = 2.5)
                    if (varType == 1 and value == defaultValue) or (varType > 1 and value == 0):
                        continue
                    if math.isnan(value):
                        if isExportInhoms:
                            value = 'math.nan'
                        else:
                            if mth.isDiamDistMechVar(mechIdx, varType, varName):
                                value = 'math.nan'
                            else:
                                continue
                    if arraySize == 1:
                        newLines.append('    mechStd.set("{}", {})'.format(varName, value))
                    else:
                        newLines.append('    mechStd.set("{}", {}, {})'.format(varName, value, arrayIndex))
                    isAllDefault = False
                    
            if isAllDefault:
                continue
                
            newLines.append('    comp.mechStds[{}][{}] = mechStd'.format(mechIdx, varTypeIdx))
            newLines.append('    ')
            
            lines.extend(newLines)
            
        return lines
        
    # For each comp, generate the call of corresponding proc
    def _finishExportOfHomogenVars(self, allComps, allCompsVarName, procNames, initProcName):
        lines = []
        
        for compIdx in range(len(allComps)):
            lines.append('comp = {}.o({})'.format(allCompsVarName, compIdx))
            procName = procNames[compIdx]
            lines.append('{}(comp)'.format(procName))
            lines.append('')
            
        lines.append('for eachItemInList(comp, {}) {{'.format(allCompsVarName))
        lines.append('    comp.{}()'.format(initProcName))
        lines.append('}')
        
        # !!! BUG: we don't export GLOBAL-s
        
        return lines
        
    def _isExportedSynComp(self, compIdx):
        is3Or1PartInSynStruc = self._hocObj.synGroup.is3Or1PartInSynStruc()
        enumSynCompIdxs = self._hocObj.enumSynCompIdxs
        if is3Or1PartInSynStruc:
            return compIdx in [enumSynCompIdxs.srcPp, enumSynCompIdxs.netCon, enumSynCompIdxs.trgPp]
        else:
            return compIdx == enumSynCompIdxs.sngPp
            