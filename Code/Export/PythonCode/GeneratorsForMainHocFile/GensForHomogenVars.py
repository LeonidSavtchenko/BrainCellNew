
import math
from neuron import h
from Utils.UnitsUtils import UnitsUtils
from Utils.OtherUtils import *


class GensForHomogenVars:
    
    def initHomogenBiophysics(self):
        if not hocObj.exportOptions.isExportDistMechs:
            return emptyParagraphHint()
            
        lines = []
        
        mmAllComps = hocObj.mmAllComps
        
        # Create number of proc-s to prepare and set "isMechInserted" and "mechStds" for each mech comp
        procNames = []
        mth = hocObj.mth
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
                newLines = self._exportHomogenVarsOfThisMech(compIdx, comp, mechIdx, hocObj.exportOptions.isExportDistMechAssignedAndState, hocObj.exportOptions.isExportDistMechInhoms)
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
        if not hocObj.exportOptions.isExportSyns:
            return emptyParagraphHint()
            
        lines = []
        
        synGroup = hocObj.synGroup
        
        mechIdxs = [None] * 4
        mechIdxs[0] = int(synGroup.getMechIdxAndOptionalName(0))    # "Source PP"
        mechIdxs[1] = 0                                             # "NetCon"
        mechIdxs[2] = int(synGroup.getMechIdxAndOptionalName(1))    # "Target PP"
        mechIdxs[3] = int(synGroup.getMechIdxAndOptionalName(2))    # "Single PP"
        
        smAllComps = hocObj.smAllComps
        
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
                newLines = self._exportHomogenVarsOfThisMech(compIdx, comp, mechIdx, hocObj.exportOptions.isExportSynAssignedAndState, hocObj.exportOptions.isExportSynInhoms)
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
        
        mth = hocObj.mth
        mcu = hocObj.mcu
        inhomAndStochLibrary = hocObj.inhomAndStochLibrary
        
        isAnyExposedVars = hocObj.exportOptions.isAnyExposedVars()
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        
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
                    isContinue, isExposedOrSweptVar, isValueNaN, valueMathNaNOrExposedOrSweptName, unitsCommentOrEmpty = self._getOneValueInfo(enumDmPpNc, compIdx, comp, mechIdx, varType, varTypeIdx, varIdx, varName, arraySize, arrayIndex, defaultMechStd, isExportInhoms, isAnyExposedVars, isAnySweptVars)
                    if isContinue:
                        continue
                    if arraySize == 1:
                        newLines.append('    mechStd.set("{}", {}){}'.format(varName, valueMathNaNOrExposedOrSweptName, unitsCommentOrEmpty))
                        if enumDmPpNc == 2 and mcu.isMetaVar(varName):
                            if isExposedOrSweptVar:
                                newLines.append(f'    seh.isMinRPlt1 = ({valueMathNaNOrExposedOrSweptName} < 1)')
                            elif isValueNaN or valueMathNaNOrExposedOrSweptName < 1:
                                newLines.append('    seh.isMinRPlt1 = 1')
                    else:
                        newLines.append('    mechStd.set("{}", {}, {}){}'.format(varName, valueMathNaNOrExposedOrSweptName, arrayIndex, unitsCommentOrEmpty))
                    isAllDefault = False
                    
            if isAllDefault:
                continue
                
            newLines.append('    comp.mechStds[{}][{}] = mechStd'.format(mechIdx, varTypeIdx))
            newLines.append('    ')
            
            lines.extend(newLines)
            
        return lines
        
    def _getOneValueInfo(self, enumDmPpNc, compIdx, comp, mechIdx, varType, varTypeIdx, varIdx, varName, arraySize, arrayIndex, defaultMechStd, isExportInhoms, isAnyExposedVars, isAnySweptVars):
    
        # !!!! need to make sure that user doesn't select the same var as both exposed and swept,
        # but selection of a fixed exposed var (e.g. "v_init" or other from hocObj.exportOptions.stdExposedVarsList) as a swept var is fine:
        # in this case, we'll use the swept value and ignore the fixed exposed value
        
        if isAnySweptVars:
            sweptVarNameOrEmpty = self._getExposedOrSweptVarNameOrEmpty(enumDmPpNc, compIdx, mechIdx, varType, varName, arrayIndex, hocObj.exportOptions.sweptVarsList, getSweptVarName)
            if sweptVarNameOrEmpty:
                return False, True, None, sweptVarNameOrEmpty, ''
                
        if isAnyExposedVars:
            exposedVarNameOrEmpty = self._getExposedOrSweptVarNameOrEmpty(enumDmPpNc, compIdx, mechIdx, varType, varName, arrayIndex, hocObj.exportOptions.exposedVarsList, getExposedVarName)
            if exposedVarNameOrEmpty:
                return False, True, None, exposedVarNameOrEmpty, ''
                
        value = comp.mechStds[mechIdx][varTypeIdx].get(varName, arrayIndex)
        
        mth = hocObj.mth
        
        # Decide whether to skip "mechStd.set" for this var;
        # for stoch vars, we don't skip it even though the value is default
        # because we'll need to read it just before adding the noise
        if not hocObj.inhomAndStochLibrary.isStochEnabledFor(enumDmPpNc, compIdx, mechIdx, varType, varIdx, arrayIndex):
            defaultValue = defaultMechStd.get(varName, arrayIndex)
            # !! not sure about the 2nd condition in IF below,
            #    but it found out for ASSIGNED "ko_IKa" from "IPotassium.mod" that its default value
            #    is different depending on the moment when we created a new MechanismStandard:
            #    just after the start of our program (defaultValue = 0) or now (defaultValue = 2.5)
            if (varType == 1 and value == defaultValue) or (varType > 1 and value == 0):
                return True, None, None, None, None
                
        unitsCommentOrEmpty = ''
        
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
                    return True, None, None, None, None
        else:
            varNameWithIndex = h.ref('')
            mth.getVarNameWithIndex(varName, arraySize, arrayIndex, varNameWithIndex)
            varNameWithIndex = varNameWithIndex[0]
            isDmOrSynPart = (comp.enumDmPpNc == 0)
            units = UnitsUtils.getUnitsForDmOrSynPart(isDmOrSynPart, compIdx, mechIdx, varName, varNameWithIndex)
            if units:
                unitsCommentOrEmpty = '    // ({})'.format(units)
                
        return False, False, isValueNaN, value, unitsCommentOrEmpty
        
    def _getExposedOrSweptVarNameOrEmpty(self, enumDmPpNc, compIdx, mechIdx, varType, varName, arrayIndex, varsList, getVarName):
        for varIdx in range(len(varsList)):
            if varsList[varIdx].isEqual(enumDmPpNc, compIdx, mechIdx, varType, varName, arrayIndex):
                return getVarName(varIdx)
        return ''
        
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
        is3Or1PartInSynStruc = hocObj.synGroup.is3Or1PartInSynStruc()
        enumSynCompIdxs = hocObj.enumSynCompIdxs
        if is3Or1PartInSynStruc:
            return compIdx in [enumSynCompIdxs.srcPp, enumSynCompIdxs.netCon, enumSynCompIdxs.trgPp]
        else:
            return compIdx == enumSynCompIdxs.sngPp
            