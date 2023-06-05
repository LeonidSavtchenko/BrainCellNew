
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
        for compIdx in range(len(mmAllComps)):
            comp = mmAllComps[compIdx]
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
                newLines = self._exportHomogenVarsOfThisMech(compIdx, comp, mechIdx, self._exportOptions.isExportDistMechAssignedAndState, self._exportOptions.isExportDistMechInhoms)
                lines.extend(newLines)
                
            lines[-1] = '}'
            lines.append('')
            
        # For each comp, generate the call of corresponding proc
        newLines = self._finishExportOfHomogenVars(mmAllComps, 'mmAllComps', procNames)
        lines.extend(newLines)
        
        lines.append('for eachItemInList(comp, mmAllComps) {')
        lines.append('    comp.initHomogenBiophysics()')
        lines.append('}')
        
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
                newLines = self._exportHomogenVarsOfThisMech(compIdx, comp, mechIdx, self._exportOptions.isExportSynAssignedAndState, self._exportOptions.isExportSynInhoms)
                lines.extend(newLines)
                
            lines[-1] = '}'
            lines.append('')
            
        # For each comp, generate the call of corresponding proc
        newLines = self._finishExportOfHomogenVars(smAllComps, 'smAllComps', procNames)
        lines.extend(newLines)
        
        return lines
        
        
    # Generate code to init "mechStds" array slice for this mech of this comp
    def _exportHomogenVarsOfThisMech(self, compIdx, comp, mechIdx, isExportAssignedAndState, isExportInhoms):
        lines = []
        
        mth = self._hocObj.mth
        mcu = self._hocObj.mcu
        inhomAndStochLibrary = self._hocObj.inhomAndStochLibrary
        
        mechName = h.ref('')
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
                    
                    # Decide whether to skip "mechStd.set" for this var;
                    # for stoch vars, we don't skip it even though the value is default
                    # because we'll need to read it just before adding the noise
                    if not self._hocObj.inhomAndStochLibrary.isStochEnabledFor(enumDmPpNc, compIdx, mechIdx, varType, varIdx, arrayIndex):
                        defaultValue = defaultMechStd.get(varName, arrayIndex)
                        # !! not sure about the 2nd condition in IF below,
                        #    but it found out for ASSIGNED "ko_IKa" from "IPotassium.mod" that its default value
                        #    is different depending on the moment when we created a new MechanismStandard:
                        #    just after the start of our program (defaultValue = 0) or now (defaultValue = 2.5)
                        if (varType == 1 and value == defaultValue) or (varType > 1 and value == 0):
                            continue
                            
                    isValueNaN = math.isnan(value)
                    if isValueNaN:
                        if isExportInhoms:
                            value = 'math.nan'
                        else:
                            if mth.isDiamDistMechVar(mechIdx, varType, varName):
                                value = 'math.nan'
                            else:
                                # If user applied an inhomogeneity to NetCon.@release_probability, but disabled export of syn inhoms,
                                # then the probability var gets effectively reverted to its default const value "1" and the 5-chain synapses become the 3-chain ones
                                # (except the case of stochasticity enabled)
                                continue
                    if arraySize == 1:
                        newLines.append('    mechStd.set("{}", {})'.format(varName, value))
                        if enumDmPpNc == 2 and mcu.isMetaVar(varName) and (isValueNaN or value < 1):
                            newLines.append('    seh.isMinRPlt1 = 1')
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
    def _finishExportOfHomogenVars(self, allComps, allCompsVarName, procNames):
        lines = []
        
        for compIdx in range(len(allComps)):
            lines.append('comp = {}.o({})'.format(allCompsVarName, compIdx))
            procName = procNames[compIdx]
            lines.append('{}(comp)'.format(procName))
            lines.append('')
            
        # !!! BUG: we don't export GLOBAL-s
        
        return lines
        
    def _isExportedSynComp(self, compIdx):
        is3Or1PartInSynStruc = self._hocObj.synGroup.is3Or1PartInSynStruc()
        enumSynCompIdxs = self._hocObj.enumSynCompIdxs
        if is3Or1PartInSynStruc:
            return compIdx in [enumSynCompIdxs.srcPp, enumSynCompIdxs.netCon, enumSynCompIdxs.trgPp]
        else:
            return compIdx == enumSynCompIdxs.sngPp
            