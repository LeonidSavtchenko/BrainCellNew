
import math
from neuron import h
from BiophysJsonExportImportUtils import BiophysJsonExportImportUtils
from OtherInterModularUtils import *


# !!! compare the units we read from JSON (including "GPassive") with the units in NEURON and show a warning if they are different

class BiophysJsonImportCore:
    
    def importCore(self, jsonDict, options):
        
        mmAllComps = hocObj.mmAllComps
        inhomAndStochLibrary = hocObj.inhomAndStochLibrary
        
        donCompNames = list(jsonDict.keys())    # "don" - donor
        
        numDonComps = len(donCompNames)
        
        for donCompIdx in range(numDonComps):
            if not options.isUseThisCompNameVec[donCompIdx]:
                continue
                
            compName = donCompNames[donCompIdx]
            
            compInfoDict = jsonDict[compName]
            
            recCompIdx = self._getRecCompIdx(compName)  # "rec" - recipient
            
            recComp = mmAllComps[recCompIdx]
            
            stickyMechNamesList_before = recComp.onJustBeforeCompHomogenBiophysImport()
            stickyMechNamesSet_imported = self._consumeDataFromCompInfoDict(recCompIdx, compInfoDict, options, 1)
            recComp.onJustAfterCompHomogenBiophysImport()
            
            # !!! would it make sense to delete all inactiveSpecVars once user clicks Apply in Vars Editor?
            # !!! what if user had actSpecVars for sticky mechs that we cannot uninsert?
            inhomAndStochLibrary.onJustBeforeCompInhomStochBiophysImport(recCompIdx)
            self._consumeDataFromCompInfoDict(recCompIdx, compInfoDict, options, 0)
            
            # !!!!!!! don't forget about special logic for verbatim inhom models
            stickyMechNames = list(name for name in stickyMechNamesList_before if name not in stickyMechNamesSet_imported)
            if stickyMechNames:
                csv = ', '.join(stickyMechNames)
                # !!!! do we need to reset mechStd for a sticky mech to defaults if it was inserted before and not imported? (currently we don't reset them)
                h.continue_dialog(f'Cannot uninsert the next mech(s) from the sections of \"{recComp.name}\" comp (NEURON restriction): {csv}.')
                
        return 0
        
        
    def _consumeDataFromCompInfoDict(self, recCompIdx, compInfoDict, options, isConsumeHomogenOrInhomStochData):
        
        mth = hocObj.mth
        
        recComp = hocObj.mmAllComps[recCompIdx]     # !!! maybe just reuse recComp obtaned upstream
        
        stickyMechNamesSet = set()
        
        for (mechName, mechInfoDict) in compInfoDict.items():
            mechIdx = int(mth.getMechIdx(0, mechName))
            if isConsumeHomogenOrInhomStochData:
                recComp.isMechInserted[mechIdx] = 1
                if mth.isDistMechSticky(mechIdx):
                    stickyMechNamesSet.add(mechName)
            for (varTypeName, varTypeInfoDict) in mechInfoDict.items():
                varType = self._getVarType(varTypeName)
                varTypeIdx = int(mth.convertVarTypeToVarTypeIdx(varType))
                if varTypeIdx > 0 and not options.isAssignedAndState:
                    continue
                allVarNames = self._getAllVarNames(mechName, varType)
                for (varNameWithIndexAndUnits, varValueOrInfoDict) in varTypeInfoDict.items():
                    (varName, arrayIndex, unitsOrEmpty) = self._parseVarNameArrayIndexAndUnits(varNameWithIndexAndUnits)
                    varIdx = self._getVarIdx(varName, allVarNames)
                    
                    if type(varValueOrInfoDict) is not dict:
                        isInhom = False
                        isStoch = False
                        varValue = varValueOrInfoDict
                    else:
                        # !!!!!!! unify underscore and camel case in node names
                        (isInhom, inhomModelInfoDictOrNone) = self._getOptionalInfoDict(varValueOrInfoDict, 'inhom_model')
                        (isStoch, stochModelInfoDictOrNone) = self._getOptionalInfoDict(varValueOrInfoDict, 'stoch_model')
                        (isBaseValue, baseVarValueOrNone) = self._getOptionalInfoDict(varValueOrInfoDict, 'baseValue')
                        if not (isInhom or isStoch):
                            codeContractViolation()
                        if not isInhom and isStoch and not isBaseValue:
                            baseVarValueOrNone = recComp.mechStds[mechIdx][varTypeIdx].get(varName, arrayIndex)     # !!!!!!!!!!!!! review this logic once again
                        varValue = baseVarValueOrNone
                        
                    if isConsumeHomogenOrInhomStochData:
                        if not isInhom:
                            # !!!!!! do we need to set it when user decides not to import stoch models?
                            self._setVarValueToMechStd(recComp, mechIdx, varTypeIdx, varName, varValue, arrayIndex)
                        continue
                        
                    if not isInhom and not isStoch:
                        # Empty by design
                        pass
                    elif isInhom and not isStoch:
                        if options.isInhoms:
                            self._importInhomModel(recCompIdx, mechIdx, varType, varIdx, arrayIndex, inhomModelInfoDictOrNone)
                    elif not isInhom and isStoch:
                        if options.isStochs:
                            self._importStochModel(recCompIdx, mechIdx, varType, varIdx, arrayIndex, stochModelInfoDictOrNone)
                    elif isInhom and isStoch:
                        if options.isInhoms:
                            self._importInhomModel(recCompIdx, mechIdx, varType, varIdx, arrayIndex, inhomModelInfoDictOrNone)
                        if options.isStochs:
                            self._importStochModel(recCompIdx, mechIdx, varType, varIdx, arrayIndex, stochModelInfoDictOrNone)
                    else:
                        codeContractViolation()
                        
        return stickyMechNamesSet
        
    def _getRecCompIdx(self, compName):
        
        mmAllComps = hocObj.mmAllComps
        
        # !!! recCompIdx = hocObj.findItemInListByString(mmAllComps, compName, 'name')
        #     if recCompIdx == -1:
        #         codeContractViolation()
        
        numRecComps = len(mmAllComps)   # Recipient
        
        for recCompIdx in range(numRecComps):
            if mmAllComps[recCompIdx].name == compName:
                return recCompIdx
                
        codeContractViolation()
        
    # See also: hoc:MechTypeHelper.getVarTypeName
    def _getVarType(self, varTypeName):
        try:
            varTypeIdx = BiophysJsonExportImportUtils.varTypeNames.index(varTypeName)
        except ValueError:
            codeContractViolation()
        return varTypeIdx + 1
        
    def _parseVarNameArrayIndexAndUnits(self, varNameWithIndexAndUnits):
        
        (varNameWithIndex, unitsOrEmpty) = self._parseRightPart(varNameWithIndexAndUnits, ' (', '')
        (varName, arrayIndex) = self._parseRightPart(varNameWithIndex, '[', 0)
        
        return varName, int(arrayIndex), unitsOrEmpty
        
    def _parseRightPart(self, string, startMarker, defaultRight):
        
        # !!! need to make this code tolerant to arbitrary spaces in the string
        idx = string.find(startMarker)
        if idx == -1:
            left = string
            right = defaultRight
        else:
            left = string[: idx]
            right = string[idx + 1 : -1]
            
        return left, right
        
    def _getAllVarNames(self, mechName, varType):
        mechStd = h.MechanismStandard(mechName, varType)    # !!!!! read it from comp ??
        
        varName = h.ref('')
        
        allVarNames = []
        
        numVars = mechStd.count()
        for varIdx in range(numVars):
            mechStd.name(varName, varIdx)
            allVarNames.append(varName[0])
            
        return allVarNames
        
    def _getVarIdx(self, varName, allVarNames):
        try:
            varIdx = allVarNames.index(varName)
        except ValueError:
            codeContractViolation()
        return varIdx
        
    def _getOptionalInfoDict(self, infoDict, optKey):
        
        try:
            infoSubDictOrNone = infoDict[optKey]
        except KeyError:
            infoSubDictOrNone = None
            
        isValue = (infoSubDictOrNone is not None)
        
        return isValue, infoSubDictOrNone
        
    def _setVarValueToMechStd(self, comp, mechIdx, varTypeIdx, varName, varValue, arrayIndex):
        comp.mechStds[mechIdx][varTypeIdx].set(varName, varValue, arrayIndex)
        
    def _importInhomModel(self, compIdx, mechIdx, varType, varIdx, arrayIndex, inhomModelInfoDict):
        
        is_g_pas_in_LargeGlia = isAstrocyteSpecificInhomVar(compIdx, mechIdx, varType, varIdx, arrayIndex)
        
        if not is_g_pas_in_LargeGlia:
            self._importInhomModelCore(compIdx, mechIdx, varType, varIdx, arrayIndex, inhomModelInfoDict)
            return
            
        varName = 'GPassive'
        varNameWithUnits = '{} ({})'.format(varName, h.units(varName))
        try:
            # !!! BUG: we'll hit KeyError by mistake if the units in JSON and NEURON are different
            GPassive_new = inhomModelInfoDict[varNameWithUnits]
        except KeyError:
            # Donor user applied a custom inhom model to g_pas in "Large Glia" using Inhomogeneity editor
            self._importInhomModelCore(compIdx, mechIdx, varType, varIdx, arrayIndex, inhomModelInfoDict)
            return
            
        # Keep in sync with hoc:InhomAndStochLibrary.onJustBeforeCompInhomStochBiophysImport
        
        distFuncHelperOrNone = hocObj.inhomAndStochLibrary.getBiophysVerbatimDistFuncHelperOrNil(compIdx, mechIdx, varType, varIdx, arrayIndex)
        if distFuncHelperOrNone is None:
            (mechName, varTypeName, varNameWithIndex) = BiophysJsonExportImportUtils.getNamesForMsg(compIdx, mechIdx, varType, varIdx, arrayIndex)
            comp = hocObj.mmAllComps[compIdx]
            h.continue_dialog(f'Cannot import "Verbatim data" inhom model for "{mechName} \ {varTypeName} \ {varNameWithIndex}" in "{comp.name}" because some other inhom model has already been applied to this var.')
            return
            
        GPassive_old = hocObj.GPassive
        g_pas_factor = GPassive_new / GPassive_old
        
        distFuncHelperOrNone.multiplyBy(g_pas_factor)
        
        self._importInhomModelInnerCore(compIdx, mechIdx, varType, varIdx, arrayIndex, None, distFuncHelperOrNone)
        
        hocObj.GPassive = GPassive_new
        
    def _importInhomModelCore(self, compIdx, mechIdx, varType, varIdx, arrayIndex, inhomModelInfoDict):
        
        segmentationHelperInfoDictOrNone = inhomModelInfoDict['segmentationHelper']
        distFuncHelperInfoDict = inhomModelInfoDict['distFuncHelper']
        
        # !!!! does user prefer to have "keep as is" segmentation mode by default on import?
        if segmentationHelperInfoDictOrNone is not None:
            distMinMaxVec = h.Vector()
            comp = hocObj.mmAllComps[compIdx]
            isDisconnected = comp.getDistRangeAsVec(distMinMaxVec)
            if isDisconnected:
                (mechName, varTypeName, varNameWithIndex) = BiophysJsonExportImportUtils.getNamesForMsg(compIdx, mechIdx, varType, varIdx, arrayIndex)
                h.continue_dialog(f'Cannot import inhomogeneity (the distance function) for "{mechName} \ {varTypeName} \ {varNameWithIndex}" in "{comp.name}" because at least one section of this compartment doesn\'t have a topological connection with the distance centre.')
                return
                
            segmentationHelper = hocObj.SegmentationHelper()
            segmentationHelper.segmentationMode = segmentationHelperInfoDictOrNone['segmentationMode']
            segmentationHelper.total_nseg = segmentationHelperInfoDictOrNone['total_nseg']
            segmentationHelper.min_nseg = segmentationHelperInfoDictOrNone['min_nseg']
            segmentationHelper.setDistRange(distMinMaxVec[1] - distMinMaxVec[0])
        else:
            # VerbatimDistFuncHelper
            segmentationHelper = None
            
        hocTemplateName = distFuncHelperInfoDict['hocTemplateName']
        distFuncHelper = eval(f'hocObj.{hocTemplateName}()')
        vecOfVals = distFuncHelperInfoDict['vecOfVals']
        listOfStrs = distFuncHelperInfoDict['listOfStrs']
        self._setImportedParams(distFuncHelper, vecOfVals, listOfStrs)
        
        distFuncCatIdx = distFuncHelperInfoDict['distFuncCatIdx']
        distFuncIdx = distFuncHelperInfoDict['distFuncIdx']
        if distFuncIdx == hocObj.dfc.verbatimDistFuncIdx:
            BiophysJsonExportImportUtils.showVerbatimModelWarning(compIdx, mechIdx, varType, varIdx, arrayIndex)
            
        self._importInhomModelInnerCore(compIdx, mechIdx, varType, varIdx, arrayIndex, segmentationHelper, distFuncHelper)
        
        hocObj.inhomAndStochLibrary.onInhomApply(0, compIdx, mechIdx, varType, varIdx, arrayIndex, segmentationHelper, distFuncHelper, distFuncCatIdx, distFuncIdx)
        
    def _importInhomModelInnerCore(self, compIdx, mechIdx, varType, varIdx, arrayIndex, segmentationHelper, distFuncHelper):
        mth = hocObj.mth
        comp = hocObj.mmAllComps[compIdx]
        mechName = h.ref('')
        mth.getMechName(0, mechIdx, mechName)
        varTypeIdx = int(mth.convertVarTypeToVarTypeIdx(varType))
        mechStd = comp.mechStds[mechIdx][varTypeIdx]
        varName = h.ref('')
        mth.getVarNameAndArraySize(0, mechIdx, varType, varIdx, varName)
        
        comp.applySegmentationAndInhomogeneity(segmentationHelper, mechName, varType, varName, arrayIndex, distFuncHelper)
        
        # !!! it's a code contract that we don't export/import "constant" inhom models
        mechStd.set(varName, math.nan, arrayIndex)
        
        comp.isMechVarTypeInhom[mechIdx][varTypeIdx] = 1
        
    def _importStochModel(self, compIdx, mechIdx, varType, varIdx, arrayIndex, stochModelInfoDict):
        colourizationHelperInfoDict = stochModelInfoDict['colourizationHelper']
        boundingHelperInfoDict = stochModelInfoDict['boundingHelper']
        stochFuncHelperInfoDict = stochModelInfoDict['stochFuncHelper']
        
        colourizationHelper = hocObj.ColourizationHelper()
        colourizationHelper.chromaticity = colourizationHelperInfoDict['chromaticity']
        colourizationHelper.colour = colourizationHelperInfoDict['colour']
        colourizationHelper.alpha = colourizationHelperInfoDict['alpha']
        colourizationHelper.consumeSettings()
        
        boundingHelper = hocObj.BoundingHelper(colourizationHelper)
        boundingHelper.where = boundingHelperInfoDict['where']
        boundingHelper.mode = boundingHelperInfoDict['mode']
        boundingHelper.min = boundingHelperInfoDict['min']
        boundingHelper.max = boundingHelperInfoDict['max']
        
        hocTemplateName = stochFuncHelperInfoDict['hocTemplateName']
        stochFuncHelper = eval(f'hocObj.{hocTemplateName}()')
        vecOfVals = stochFuncHelperInfoDict['vecOfVals']
        listOfStrs = stochFuncHelperInfoDict['listOfStrs']
        self._setImportedParams(stochFuncHelper, vecOfVals, listOfStrs)
        
        stochFuncCatIdx = stochFuncHelperInfoDict['stochFuncCatIdx']
        stochFuncIdx = stochFuncHelperInfoDict['stochFuncIdx']
        
        hocObj.inhomAndStochLibrary.onStochApply(0, compIdx, mechIdx, varType, varIdx, arrayIndex, boundingHelper, stochFuncHelper, stochFuncCatIdx, stochFuncIdx)
        
    # See also: BiophysJsonExportCore._getExportedParams
    def _setImportedParams(self, distOrStochFuncHelper, vecOfVals, listOfStrs):
        
        vecOfVals = h.Vector(vecOfVals)
        listOfStrs = convertPyIterableOfStrsToHocListOfStrObjs(listOfStrs)
        
        distOrStochFuncHelper.importParams(vecOfVals, listOfStrs)
        