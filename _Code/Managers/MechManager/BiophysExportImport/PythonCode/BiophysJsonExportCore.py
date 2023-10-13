
import math
from neuron import h
from BiophysJsonExportImportUtils import BiophysJsonExportImportUtils
from OtherInterModularUtils import *


class BiophysJsonExportCore:
    
    _options = None
    
    
    def exportCore(self, options):
        
        mmAllComps = hocObj.mmAllComps
        
        jsonDict = {}
        
        self._options = options
        
        numComps = mmAllComps.count()
        for compIdx in range(numComps):
            if not options.isUseThisCompNameVec[compIdx]:
                continue
            compInfoDict = self._prepareCompInfoDictOrEmpty(compIdx)
            if not compInfoDict:
                continue
            compName = mmAllComps[compIdx].name
            jsonDict[compName] = compInfoDict
            
        self._options = None
        
        return jsonDict
        
        
    def _prepareCompInfoDictOrEmpty(self, compIdx):
        
        mth = hocObj.mth
        comp = hocObj.mmAllComps[compIdx]
        
        mechName = h.ref('')
        
        jsonDict = {}
        
        numMechs = int(mth.getNumMechs(0))
        for mechIdx in range(numMechs):
            if mechIdx == mth.morphologyMechIdx or not comp.isMechInserted[mechIdx]:
                continue
            mechInfoDict = self._prepareMechInfoDictOrEmpty(compIdx, mechIdx)
            # Empty mechInfoDict means "mech is inserted, but all vars are default"
            mth.getMechName(0, mechIdx, mechName)
            jsonDict[mechName[0]] = mechInfoDict
            
        return jsonDict
        
    def _prepareMechInfoDictOrEmpty(self, compIdx, mechIdx):
        
        mth = hocObj.mth
        
        jsonDict = {}
        
        # !!! we can create varTypes once before all the cycles
        varTypes = [1]                  # 1: PARAMETER
        if self._options.isAssignedAndState:
            varTypes.extend([2, 3])     # 2: ASSIGNED, 3: STATE
            
        for varType in varTypes:
            varTypeInfoDict = self._prepareVarTypeInfoDictOrEmpty(compIdx, mechIdx, varType)
            if not varTypeInfoDict:
                continue
            varTypeName = h.ref('')
            mth.getVarTypeName(varType, varTypeName)
            jsonDict[varTypeName[0]] = varTypeInfoDict
            
        return jsonDict
        
    def _prepareVarTypeInfoDictOrEmpty(self, compIdx, mechIdx, varType):
        
        mth = hocObj.mth
        
        mechName = h.ref('')
        mth.getMechName(0, mechIdx, mechName)
        
        # !!! maybe there is no need to create this for ASSIGNED and STATE because we know that defaultValue for them is 0
        defaultMechStd = h.MechanismStandard(mechName, varType)
        
        varName = h.ref('')             # !!! maybe just save this one in the class and reuse in _prepareVarInfoDictOrEmpty
        varNameWithIndexAndUnits = h.ref('')
        
        jsonDict = {}
        
        numVars = int(mth.getNumMechVars(0, mechIdx, varType))
        for varIdx in range(numVars):
            arraySize = int(mth.getVarNameAndArraySize(0, mechIdx, varType, varIdx, varName))
            for arrayIndex in range(arraySize):
                varInfoDict = self._prepareVarInfoDictOrEmpty(compIdx, mechIdx, varType, varIdx, arrayIndex, defaultMechStd)
                if not varInfoDict:
                    continue
                mth.getVarNameWithIndexAndUnits(0, mechIdx, varName[0], arraySize, arrayIndex, varNameWithIndexAndUnits)
                jsonDict[varNameWithIndexAndUnits[0]] = varInfoDict
                
        return jsonDict
        
    def _prepareVarInfoDictOrEmpty(self, compIdx, mechIdx, varType, varIdx, arrayIndex, defaultMechStd):
        
        mth = hocObj.mth
        inhomAndStochLibrary = hocObj.inhomAndStochLibrary
        comp = hocObj.mmAllComps[compIdx]
        
        varName = h.ref('')
        mth.getVarNameAndArraySize(0, mechIdx, varType, varIdx, varName)
        
        isInhom1 = inhomAndStochLibrary.isInhomEnabledFor(0, compIdx, mechIdx, varType, varIdx, arrayIndex)
        isInhom2 = comp.isMechVarInhom(mechIdx, varType, varName, arrayIndex)
        if isInhom1 != isInhom2:
            codeContractViolation()
        isInhom = isInhom1
        
        isStoch = inhomAndStochLibrary.isStochEnabledFor(0, compIdx, mechIdx, varType, varIdx, arrayIndex)
        
        varTypeIdx = int(mth.convertVarTypeToVarTypeIdx(varType))
        varValue = comp.mechStds[mechIdx][varTypeIdx].get(varName, arrayIndex)
        
        defaultValue = defaultMechStd.get(varName, arrayIndex)
        if math.isnan(defaultValue):
            # !!! risky for arbitrary user mechs
            codeContractViolation()
            
        jsonDict = {}
        
        if not isInhom and not isStoch:
            if math.isnan(varValue):
                codeContractViolation()
            if varValue != defaultValue:
                jsonDict = varValue
        elif isInhom and not isStoch:
            if self._options.isInhoms:
                jsonDict['inhom_model'] = self._prepareInhomModelInfoDict(compIdx, mechIdx, varType, varIdx, arrayIndex)
        elif not isInhom and isStoch:
            if math.isnan(varValue):
                codeContractViolation()
            if self._options.isStochs:
                if varValue != defaultValue:
                    jsonDict['baseValue'] = varValue
                jsonDict['stoch_model'] = self._prepareStochModelInfoDict(compIdx, mechIdx, varType, varIdx, arrayIndex)
            elif varValue != defaultValue:
                jsonDict = varValue
        else:
            if self._options.isInhoms:
                jsonDict['inhom_model'] = self._prepareInhomModelInfoDict(compIdx, mechIdx, varType, varIdx, arrayIndex)
            if self._options.isStochs:
                jsonDict['stoch_model'] = self._prepareStochModelInfoDict(compIdx, mechIdx, varType, varIdx, arrayIndex)
                
        return jsonDict
        
    def _prepareInhomModelInfoDict(self, compIdx, mechIdx, varType, varIdx, arrayIndex):
        
        # !!! do we really need to export/import segmentationHelper as a part of biophysics?
        #     (does user prefer to have "keep as is" segmentation mode by default on import?)
        # !!!!! be careful importing VerbatimDistFuncHelper
        
        actSpecVar = hocObj.inhomAndStochLibrary.findActiveSpecVar(0, compIdx, mechIdx, varType, varIdx, arrayIndex)
        
        cond = (getTemplateName(actSpecVar.distFuncHelper) == 'VerbatimDistFuncHelper' and
            isAstrocyteSpecificInhomVar(compIdx, mechIdx, varType, varIdx, arrayIndex))
            
        if not cond:
            jsonDict = self._prepareInhomModelInfoDictCore(actSpecVar)
        else:
            varName = 'GPassive'
            varNameWithUnits = '{} ({})'.format(varName, h.units(varName))
            jsonDict = { varNameWithUnits: hocObj.GPassive }
            
        return jsonDict
        
    def _prepareInhomModelInfoDictCore(self, actSpecVar):
        
        segmentationHelper = actSpecVar.segmentationHelper
        distFuncHelper = actSpecVar.distFuncHelper
        
        vecOfVals, listOfStrs = self._getExportedParams(distFuncHelper)
        
        if segmentationHelper is not None:
            segmentationHelperInfoDict = {
                'segmentationMode': int(segmentationHelper.segmentationMode),
                'total_nseg': int(segmentationHelper.total_nseg),
                'min_nseg': int(segmentationHelper.min_nseg) }
        else:
            # VerbatimDistFuncHelper
            segmentationHelperInfoDict = None
            
        # !!! for encapsulation, maybe implement actSpecVar.toJson which, in turn, will call .toJson for all nested objects;
        #     also, implement actSpecVar.fromJson
        
        if actSpecVar.distFuncIdx == hocObj.dfc.verbatimDistFuncIdx:
            BiophysJsonExportImportUtils.showVerbatimModelWarning(actSpecVar.compIdx, actSpecVar.mechIdx, actSpecVar.varType, actSpecVar.varIdx, actSpecVar.arrayIndex)
            
        jsonDict = {
            'distFuncHelper': {
                'hocTemplateName': getTemplateName(distFuncHelper),
                'distFuncCatIdx': int(actSpecVar.distFuncCatIdx),
                'distFuncIdx': int(actSpecVar.distFuncIdx),
                'vecOfVals': vecOfVals,
                'listOfStrs': listOfStrs },
            'segmentationHelper': segmentationHelperInfoDict }
            
        return jsonDict
        
    def _prepareStochModelInfoDict(self, compIdx, mechIdx, varType, varIdx, arrayIndex):
        
        actSpecVar = hocObj.inhomAndStochLibrary.findActiveSpecVar(0, compIdx, mechIdx, varType, varIdx, arrayIndex)
        
        boundingHelper = actSpecVar.boundingHelper
        stochFuncHelper = actSpecVar.stochFuncHelper
        
        colourizationHelper = boundingHelper.colourizationHelper
        
        vecOfVals, listOfStrs = self._getExportedParams(stochFuncHelper)
        
        # !!! for encapsulation, maybe implement actSpecVar.toJson which, in turn, will call .toJson for all nested objects;
        #     also, implement actSpecVar.fromJson
        
        jsonDict = {
            'stochFuncHelper': {
                'hocTemplateName': getTemplateName(stochFuncHelper),
                'stochFuncCatIdx': int(actSpecVar.stochFuncCatIdx),
                'stochFuncIdx': int(actSpecVar.stochFuncIdx),
                'vecOfVals': vecOfVals,
                'listOfStrs': listOfStrs },
            'boundingHelper': {
                'where': int(boundingHelper.where),
                'mode': int(boundingHelper.mode),
                'min': boundingHelper.min,
                'max': boundingHelper.max },
            'colourizationHelper': {
                'chromaticity': int(colourizationHelper.chromaticity),
                'colour': int(colourizationHelper.colour),
                'alpha': colourizationHelper.alpha } }
                
        return jsonDict
        
    # See also: BiophysJsonImportCore._setImportedParams
    def _getExportedParams(self, distOrStochFuncHelper):
        
        vecOfVals = h.Vector()
        listOfStrs = h.List()
        distOrStochFuncHelper.exportParams(vecOfVals, listOfStrs)
        
        vecOfVals = list(vecOfVals)
        listOfStrs = list(item.s for item in listOfStrs)
        
        return vecOfVals, listOfStrs
        