
import os
from neuron import h, hoc, nrn
from OtherUtils import *


class Generators:
    
    _defaultNseg = 1
    _defaultRa = 35.4
    
    _hocObj = hoc.HocObject()
    
    # Other data members that will be added in the ctor:
    #   _exportOptions
    
    def __init__(self):
        self._exportOptions = self._hocObj.exportOptions
        
    def getAllCreateStatementsExceptNanogeometry(self):
        # input:  allNames (List of String-s, taken from the top level)
        # output: a string like 'create name1, name2[123], name3[456][7], ...'
        
        if len(self._hocObj.allNames) == 0:
            codeContractViolation()
        
        createdNames = []
        for name in self._hocObj.allNames:
            createdName = name.s
            
            # !! update this logic once I correct\\replace getAllSectionNames which produces allNames
            if createdName == 'AstrocyteNanoBranch' or createdName == 'NeuronNanoBranch':   # !! hardcode
                continue
                
            secObj = self._getHocVar(createdName)
            while True:
                isSecObjOrArray = self._isSecObjOrArray(secObj)
                if isSecObjOrArray:
                    break
                else:
                    createdName += '[{}]'.format(len(secObj))
                    secObj = secObj[0]
                    
            createdNames.append(createdName)
            
        resStr = 'create ' + ', '.join(createdNames)
        
        return resStr
        
    def createListOfSectionRef(self, usedNamesHocListName, secRefHocListName):
        allLines = []
        newLine = '{} = new List()'.format(secRefHocListName)
        allLines.append(newLine)
        for usedNameHocString in self._getHocVar(usedNamesHocListName):
            usedName = usedNameHocString.s
            secObj = self._getHocVar(usedName)
            isSecObjOrArray = self._isSecObjOrArray(secObj)
            if isSecObjOrArray:
                newLine = '{} {}.append(new SectionRef())'.format(usedName, secRefHocListName)
                allLines.append(newLine)
            else:
                newLines = [
                    'for idx = 0, {} - 1 {{'.format(len(secObj)),
                    '    {}[idx] {}.append(new SectionRef())'.format(usedName, secRefHocListName),
                    '}']
                allLines.extend(newLines)
        return allLines
        
    # !! maybe split topology by blocks for soma, dendrites, axon, nanogeometry, other
    def initTopology(self):
        lines = []
        for sec in h.allsec():
            secRef = h.SectionRef(sec)
            if not secRef.has_parent():
                continue
            # Some comments:
            # 1. The syntax "connect child(x), parent(y)" looks simpler than "parent connect child(x), y",
            #    but the former does not work for the sections owned by templates (all nanogeometry in our case)
            # 2. The syntax "sec=sec" is important here; do not replace it with "sec", because the called methods will always return 0
            # 3. Max. precision is applied in the next line by Python automatically
            line = '{} connect {}({}), {}'.format(secRef.parent.name(), sec.name(), h.section_orientation(sec=sec), h.parent_connection(sec=sec))
            lines.append(line)
        return lines
        
    # !! for file "Geometry\Neuron\test.hoc", we have:
    #    AstrocyteNanoBranch[0].SmallGlia[0] { ... pt3dadd(0.075074203312397, -0.07739131152629852, 0.0, 0.10000000149011612
    #    why garbage in diam?
    # !! for file "Geometry\Astrocyte\New Style\AstrocyteBasicGeometry.hoc", we have:
    #    soma[0] { ... pt3dadd(0.23000000417232513, 5.829999923706055, 0.0, 7.22599983215332)
    #    why garbage in x?
    # !! for file "Geometry\Neuron\cellmorphology.hoc", the value of "y" passed to "pt3dadd" is unstable,
    #    i.e. it varies from one export to other
    # !! maybe split geometry by blocks for soma, dendrites, axon, nanogeometry, other
    # !! investigate at which stage of the program the 3D-coordinates of 1st point of 1st imported dendrite become changed (at least in the next files: AstrocyteBasicGeometry.hoc и cellmorphology.hoc)
    #    "connect" command does not change them, so maybe finitialize?
    def initGeometry(self):
        lines = []
        for sec in h.allsec():
            line = '{} {{'.format(sec.name())
            lines.append(line)
            lines.append('    pt3dclear()') # Almost sure that not needed, but Cell Builder's Exporter adds this
            for ptIdx in range(sec.n3d()):
                # Max. precision is applied here automatically
                line = '    pt3dadd({}, {}, {}, {})'.format(sec.x3d(ptIdx), sec.y3d(ptIdx), sec.z3d(ptIdx), sec.diam3d(ptIdx))
                lines.append(line)
            if sec.nseg != self._defaultNseg:
                line = '    nseg = {}'.format(sec.nseg)
                lines.append(line)
            if sec.Ra != self._defaultRa:
                line = '    Ra = {}'.format(sec.Ra)
                lines.append(line)
            lines.append('}')
        return lines
        
    # !!! remove this block once we export the random g_pas in LargeGlia
    def initAstrocyteNanogeometryBiophysics(self):
        if not self._hocObj.isAstrocyteOrNeuron:
            codeContractViolation()
            
        if not self._exportOptions.isExportDistMechs:
            return emptyParagraphHint()
            
        lines = []
        
        lines.append(self.getDoubleValueFromTopLevel('GPassive'))
        lines.append(self.getIntegerValueFromTopLevel('currentMechanismSetup'))
        lines.append(self.getDoubleValueFromTopLevel('DensityGluTransporters'))
        lines.append('')
        
        newLines = self.insertAllLinesFromFile('Code\\NanoCore\\Astrocyte\\Exported\\AstrocyteNanoBranch_Exported.hoc')
        lines.extend(newLines)
        lines.append('')
        
        lines.append('for idx = 0, NumberNanoBranches - 1 {')
        lines.append('    initAstrocyteBiophysics(astrocyteNanoBranch[idx])')
        lines.append('}')
        
        return lines
        
    # !! BUG: In rare cases, an error "procedure too big" may occur when user loads the exported file.
    #         This error takes place while sourcing one of obfunc-s named "getListOfSecRefsFor*Comp".
    #         The root cause is that the base geometry file imported earlier
    #         created so many sections on the top level, that we cannot create now in the scope of just one obfunc.
    #         To fix this error, we'll have to init all list_ref-s on the top level rather than in the obfunc-s.
    def createReducedMechComps(self):
    
        if not self._exportOptions.isExportDistMechs:
            fileName = 'ReducedMechComp1.hoc'   # name, list_ref
        else:
            fileName = 'ReducedMechComp2.hoc'   # name, list_ref, isMechInserted, mechStds
        lines = self.insertAllLinesFromReducedVersionFile(fileName)
        lines.append('')
        
        mmAllComps = self._hocObj.mmAllComps
        
        # Create number of obfunc-s to prepare "list_ref" for each comp
        obfuncNames = []
        for comp in mmAllComps:
            obfuncNameId = self._prepareUniqueNameId(comp.name)
            obfuncName = 'getListOfSecRefsFor{}Comp'.format(obfuncNameId)
            obfuncNames.append(obfuncName)
            lines.append('obfunc {}() {{ local idx1, idx2 localobj list_ref'.format(obfuncName))
            lines.append('    list_ref = new List()')
            newLines = []
            for sec_ref in comp.list_ref:
                newLines.append('    {} list_ref.append(new SectionRef())'.format(sec_ref.sec))
            newLines = self._insertLoopsToShorten(newLines)
            lines.extend(newLines)
            lines.append('    return list_ref')
            lines.append('}')
            lines.append('')
        
        lines.append('objref mmAllComps, comp')
        lines.append('mmAllComps = new List()')
        lines.append('')
        
        for (comp, obfuncName) in zip(mmAllComps, obfuncNames):
            lines.append('comp = new ReducedMechComp("{}", {}())'.format(comp.name, obfuncName))
            lines.append('{ mmAllComps.append(comp) }')
            lines.append('')
            
        return lines
        
    def initHomogenBiophysics(self):
        if not self._exportOptions.isExportDistMechs:
            return emptyParagraphHint()
            
        lines = []
        
        mmAllComps = self._hocObj.mmAllComps
        
        # Create number of proc-s to prepare and set "isMechInserted" and "mechStds" for each comp
        procNames = []
        mth = self._hocObj.mth
        enumDmPpNc = 0
        for comp in mmAllComps:
            procNameId = self._prepareUniqueNameId(comp.name)
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
                mechName = h.ref('')
                mth.getMechName(enumDmPpNc, mechIdx, mechName)
                mechName = mechName[0]
                if self._exportOptions.isExportDistMechAssignedAndState:
                    maxVarType = 3
                else:
                    maxVarType = 1
                for varType in range(1, maxVarType + 1):    # 1: "PARAMETER", 2: "ASSIGNED", 3: "STATE"
                    varTypeIdx = int(mth.convertVarTypeToVarTypeIdx(varType))
                    varTypeName = h.ref('')
                    mth.getVarTypeName(varType, varTypeName)
                    varTypeName = varTypeName[0]
                    defaultMechStd = h.MechanismStandard(mechName, varType)
                    newLines = []
                    isAllDefault = True
                    newLines.append('    mechStd = new MechanismStandard("{}", {})    // {}'.format(mechName, varType, varTypeName))
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
                            # !! BUG: When user turns off the export of inhom models in _exportOptions, we still assign "nan" here
                            if arraySize == 1:
                                newLines.append('    mechStd.set("{}", {})'.format(varName, value))
                            else:
                                newLines.append('    mechStd.set("{}", {}, {})'.format(varName, value, arrayIndex))
                            isAllDefault = False
                    newLines.append('    comp.mechStds[{}][{}] = mechStd'.format(mechIdx, varTypeIdx))
                    newLines.append('    ')
                    if not isAllDefault:
                        lines.extend(newLines)
            lines[-1] = '}'
            lines.append('')
            
        for compIdx in range(len(mmAllComps)):
            lines.append('comp = mmAllComps.o({})'.format(compIdx))
            procName = procNames[compIdx]
            lines.append('{}(comp)'.format(procName))
            lines.append('')
            
        lines.append('for compIdx = 0, mmAllComps.count() - 1 {')
        lines.append('    comp = mmAllComps.o(compIdx)')
        lines.append('    comp.initHomogenBiophysics()')
        lines.append('}')
        
        # !!! BUG: we don't export GLOBAL-s
        
        return lines
        
    def createInhomAndStochLibrary(self):
        if not (self._exportOptions.isExportAnyDistFuncs() or self._exportOptions.isExportAnyStochFuncs()):
            return emptyParagraphHint()
            
        lines = []
        
        newLines = self.insertAllLinesFromReducedVersionFile('ReducedInhomAndStochTarget.hoc')
        lines.extend(newLines)
        lines.append('')
        
        newLines = self.insertAllLinesFromReducedVersionFile('ReducedInhomAndStochLibrary.hoc')
        lines.extend(newLines)
        lines.append('')
        
        lines.append('objref actSpecVar')
        
        return lines
        
    def createReducedSynComps(self):
        if not self._exportOptions.isExportSyns:
            return emptyParagraphHint()
            
        lines = self.insertAllLinesFromReducedVersionFile('ReducedSynPPComp.hoc')
        lines.append('')
        
        # !!
        
        return lines
        
    # !! some code dupl. with insertAllUsedStochFuncs
    def insertAllUsedDistFuncs(self):
        if not self._exportOptions.isExportAnyDistFuncs():
            return emptyParagraphHint()
            
        lines = []
        
        distFuncCatIdxToFileNameDict = {}
        distFuncCatIdxToFileNameDict[0] = 'SimpleModelDistFuncHelper.hoc'
        distFuncCatIdxToFileNameDict[1] = 'CustomCodeDistFuncHelper.hoc'
        distFuncCatIdxToFileNameDict[2] = 'CodeFromFileDistFuncHelper.hoc'
        distFuncCatIdxToFileNameDict[3] = 'TablePlusLinInterpDistFuncHelper.hoc'
        distFuncCatIdxToFileNameDict[4] = 'SpecialDistFuncHelper.hoc'
        # !!! distFuncCatIdxToFileNameDict[!!5] = 'VerbatimDistFuncHelper.hoc'
        
        distFuncCatIdxs = set()
        for activeSpecVar in h.inhomAndStochLibrary.activeSpecVars:
            if not self._exportOptions.isExportedInhomVar(activeSpecVar):
                continue
            distFuncCatIdxs.add(activeSpecVar.distFuncCatIdx)
            
        relDirPath = 'Code\\Managers\\InhomAndStochLibrary\\InhomModels\\DistFuncHelpers\\Exported'
        self._exportSomeFilesFromThisDir(lines, relDirPath, distFuncCatIdxs, distFuncCatIdxToFileNameDict)
        lines.append('')
        
        if self._exportOptions.isExportAnyInhomBiophysModels():
            newLines = self.insertAllLinesFromReducedVersionFile('ReducedSegmentationHelper.hoc')
            lines.extend(newLines)
            
        return self._linesOrEmptyParagraphHint(lines)
        
    # !! some code dupl. with insertAllUsedDistFuncs
    def insertAllUsedStochFuncs(self):
        if not self._exportOptions.isExportAnyStochFuncs():
            return emptyParagraphHint()
            
        lines = []
        
        stochFuncIdxToFileNameDict = {}
        stochFuncIdxToFileNameDict[0] = 'UniformDistHelper.hoc'
        stochFuncIdxToFileNameDict[1] = 'NormalDistHelper.hoc'
        stochFuncIdxToFileNameDict[2] = 'LogNormalDistHelper.hoc'
        stochFuncIdxToFileNameDict[3] = 'NegExpDistHelper.hoc'
        stochFuncIdxToFileNameDict[4] = 'ErlangDistHelper.hoc'
        stochFuncIdxToFileNameDict[5] = 'WeibullDistHelper.hoc'
        
        stochFuncCatIdxToFileNameDict = {}
        stochFuncCatIdxToFileNameDict[0] = 'SimpleModelStochFuncHelper.hoc'
        stochFuncCatIdxToFileNameDict[1] = 'CustomCodeDistFuncHelper.hoc'           # v !! just stubs
        stochFuncCatIdxToFileNameDict[2] = 'CodeFromFileDistFuncHelper.hoc'
        stochFuncCatIdxToFileNameDict[3] = 'TablePlusLinInterpDistFuncHelper.hoc'   # ^ !! just stubs
        stochFuncCatIdxToFileNameDict[4] = 'SpecialStochFuncHelper.hoc'
        
        stochFuncCatIdxs = set()
        stochFuncIdxs = set()
        for activeSpecVar in h.inhomAndStochLibrary.activeSpecVars:
            if not self._exportOptions.isExportedStochVar(activeSpecVar):
                continue
            stochFuncCatIdx = activeSpecVar.stochFuncCatIdx
            stochFuncCatIdxs.add(stochFuncCatIdx)
            if stochFuncCatIdx == 0:
                stochFuncIdxs.add(activeSpecVar.stochFuncIdx)
            
        # !!! just a temp solution (we need to bind these names as templates' external-s even though they won't be used)
        lines.append('objref callPythonFunction, definePythonFunction, inhomAndStochApplicator, joinStrings, loadPythonFile, math, mwh, printMsgAndRaiseError, rngUtils, selectDistFuncInputFile, specMath, stochTestGraph')
        lines.append('iterator eachPointInGrid() { codeContractViolation() }')
        lines.append('')
        
        relDirPath = 'Code\\Managers\\InhomAndStochLibrary\\StochModels\\StochDistHelpers\\Exported'
        self._exportSomeFilesFromThisDir(lines, relDirPath, stochFuncIdxs, stochFuncIdxToFileNameDict)
        
        relDirPath = 'Code\\Managers\\InhomAndStochLibrary\\StochModels\\StochFuncHelpers\\Exported'
        self._exportSomeFilesFromThisDir(lines, relDirPath, stochFuncCatIdxs, stochFuncCatIdxToFileNameDict)
        
        return self._linesOrEmptyParagraphHint(lines)
        
    def createInhomBiophysModels(self):
        if not self._exportOptions.isExportAnyInhomBiophysModels():
            return emptyParagraphHint()
            
        lines = []
        
        lines.append('objref segmentationHelper, distFuncHelper, vecOfVals, listOfStrs')
        lines.append('')
        for activeSpecVar in h.inhomAndStochLibrary.activeSpecVars:
            if not self._exportOptions.isExportedInhomBiophysVar(activeSpecVar):
                continue
            distFuncHelper = activeSpecVar.distFuncHelper
            segmentationHelper = activeSpecVar.segmentationHelper
            
            lines.append('segmentationHelper = new ReducedSegmentationHelper()')
            lines.append('segmentationHelper.segmentationMode = {}'.format(int(segmentationHelper.segmentationMode)))
            lines.append('segmentationHelper.total_nseg = {}'.format(int(segmentationHelper.total_nseg)))
            lines.append('segmentationHelper.min_nseg = {}'.format(int(segmentationHelper.min_nseg)))
            
            # !! BUG: CodeFromFileDistFuncHelper and TablePlusLinInterpDistFuncHelper require different approaches here
            templName = self._getTemplateName(distFuncHelper)
            lines.append('distFuncHelper = new {}({}, nil)'.format(templName, int(distFuncHelper.modelIdx)))
            lines.append('vecOfVals = new Vector()')
            vecOfVals = h.Vector()
            listOfStrs = h.List()
            distFuncHelper.exportParams(vecOfVals, listOfStrs)
            for value in vecOfVals:
                lines.append('{{ vecOfVals.append({}) }}'.format(value))    # Max. precision is applied here automatically
            lines.append('listOfStrs = new List()')
            for string in listOfStrs:
                lines.append('{{ listOfStrs.append(new String("{}")) }}'.format(string.s))
            lines.append('{ distFuncHelper.importParams(vecOfVals, listOfStrs) }')
            lines.append('actSpecVar = new ReducedInhomAndStochTarget({}, {}, {}, {}, {}, {})'.format(int(activeSpecVar.enumDmPpNc), int(activeSpecVar.compIdx), int(activeSpecVar.mechIdx), int(activeSpecVar.varType), int(activeSpecVar.varIdx), int(activeSpecVar.arrayIndex)))
            lines.append('{{ actSpecVar.makeInhom(segmentationHelper, distFuncHelper, {}, {}) }}'.format(int(activeSpecVar.distFuncCatIdx), int(activeSpecVar.distFuncIdx)))
            lines.append('{ inhomAndStochLibrary.activeSpecVars.append(actSpecVar) }')
            lines.append('')
            
        lines.append('for actSpecVarIdx = 0, inhomAndStochLibrary.activeSpecVars.count() - 1 {')
        lines.append('    inhomAndStochLibrary.activeSpecVars.o(actSpecVarIdx).applyBiophysInhomogeneity()')
        lines.append('}')
        
        return lines
        
    def createStochBiophysModels(self):
        if not self._exportOptions.isExportAnyStochBiophysModels():
            return emptyParagraphHint()
            
        lines = []
        
        lines.append('// !! not implemented')
        
        # for activeSpecVar in h.inhomAndStochLibrary.activeSpecVars:
        #     if not self._exportOptions.isExportedStochBiophysVar(activeSpecVar):
        #         continue
        #     !!
        
        return lines
        
    def createInhomSynModels(self):
        if not self._exportOptions.isExportAnyInhomSynModels():
            return emptyParagraphHint()
            
        lines = []
        
        lines.append('// !! not implemented')
        
        # for activeSpecVar in h.inhomAndStochLibrary.activeSpecVars:
        #     if not self._exportOptions.isExportedInhomSynVar(activeSpecVar):
        #         continue
        #     !!
        
        return lines
        
    def createStochSynModels(self):
        if not self._exportOptions.isExportAnyStochSynModels():
            return emptyParagraphHint()
            
        lines = []
        
        lines.append('// !! not implemented')
        
        # for activeSpecVar in h.inhomAndStochLibrary.activeSpecVars:
        #     if not self._exportOptions.isExportedStochSynVar(activeSpecVar):
        #         continue
        #     !!
        
        return lines
        
    def insertAltRunControlWidget(self):
        if not self._exportOptions.isExportAnyStochFuncs():
            return emptyParagraphHint()
            
        lines = self.insertAllLinesFromFile('Code\\Core\\Widgets\\Exported\\alt_stdrun.hoc')
        lines.append('')
        
        newLines = self.insertAllLinesFromFile('Code\\Core\\Widgets\\Exported\\AltRunControlWidget.hoc')
        lines.extend(newLines)
        lines.append('')
        
        lines.append('objref altRunControlWidget')
        lines.append('altRunControlWidget = new AltRunControlWidget()')
        lines.append('altRunControlWidget.show()')
        
        return lines
        
    def insertAllLinesFromFile(self, relFilePathName):
        absFilePathName = os.getcwd() + '\\' + relFilePathName
        with open(absFilePathName, 'r') as inFile:
            inText = inFile.read()
        return inText.strip().splitlines()  # All newline characters are removed here
        
    def insertAllLinesFromReducedVersionFile(self, fileName):
        relFilePathName = 'Code\\Export\\OutHocFileStructures\\ReducedVersions\\' + fileName
        return self.insertAllLinesFromFile(relFilePathName)
        
    def getIntegerValueFromTopLevel(self, varName):
        return self._generateAssignment(varName, True)
        
    def getDoubleValueFromTopLevel(self, varName):
        return self._generateAssignment(varName, False)
        
        
    def _getHocVar(self, varName):
        return eval('self._hocObj.' + varName)  # !! maybe can do it via refletion
        
    def _generateAssignment(self, varName, isIntegerOrDouble):
        value = self._getHocVar(varName)
        if isIntegerOrDouble:
            value = int(value)
        return '{} = {}'.format(varName, value)
        
    def _isSecObjOrArray(self, secObj):
        tp = type(secObj)
        # !! we could use "match-case" here, but it was introduced only in Python 3.10 (2021),
        #    and user may have an older version installed
        if tp == nrn.Section:
            return 1
        elif tp == hoc.HocObject:
            return 0
        else:
            codeContractViolation()
            
    def _prepareUniqueNameId(self, name):
        if len(name) == 0 or name[0] == ' ' or name[-1] == ' ' or '  ' in name:
            # Keep in sync with hoc:chooseUniqueNameForCompartmentForMechManager
            codeContractViolation()
        # !! BUG: Two different names "A1" and "A 1" will have the same ID
        return name.replace(' ', '')
        
    # !! Currenly this method cannot produce the nested loops of depth 3 and higher.
    #    The depth 2 is sufficient to export astrocyte nanogeometry in the shortest way,
    #    but in general case it's not enough because the imported geometry file may store the sections
    #    in arbitrary n-dimentional structures
    def _insertLoopsToShorten(self, lines):
        lines, isShortened = self._insertLoopsToShortenCore(lines, 'idx2', False)
        
        if isShortened:
            lines2 = self._wrapInnerCycles(lines)
            lines2, isShortened = self._insertLoopsToShortenCore(lines2, 'idx1', True)
            if isShortened:
                lines = self._unwrapInnerCycles(lines2)
            
        return lines
        
    def _insertLoopsToShortenCore(self, lines, idxVarName, isSecondIteration):
    
        outLines = []
        
        isShortened = False
        
        isInsideBlock = False
        firstParsedIdx = -1
        prevParsedIdx = -1
        prevLine = ''
        prevParsedPattern = ''
        
        # !! it would be better to sort lines here because user could Merge/Split compartments and so shuffle the sections,
        #    but simple "sorted(lines)" won't work until we prepend each index with zeros so that all corresponding indices
        #    have the same length
        for line in lines:
            idx2 = self._rfindExt(line, ']', isSecondIteration)
            if idx2 == -1:
                if isInsideBlock:
                    isShortened = self._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName) or isShortened
                    isInsideBlock = False
                outLines.append(line)
                continue
            idx1 = self._rfindExt(line, '[', isSecondIteration)
            if idx1 == -1:
                codeContractViolation()
            idx1 += 1
            thisParsedIdx = int(line[idx1 : idx2])
            thisParsedPattern = '{}{}{}'.format(line[: idx1], idxVarName, line[idx2 :])
            if not isInsideBlock:
                # Found a new block
                firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern = self._startBlock(thisParsedIdx, line, thisParsedPattern)
                isInsideBlock = True
            else:
                if thisParsedPattern == prevParsedPattern and thisParsedIdx == prevParsedIdx + 1:
                    # Continue parsing this block
                    prevParsedIdx = thisParsedIdx
                else:
                    # The block is over
                    isShortened = self._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName) or isShortened
                    firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern = self._startBlock(thisParsedIdx, line, thisParsedPattern)
                    isInsideBlock = True
        
        if isInsideBlock:
            isShortened = self._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName) or isShortened
        
        return outLines, isShortened
        
    def _startBlock(self, thisParsedIdx, line, thisParsedPattern):
        return thisParsedIdx, thisParsedIdx, line, thisParsedPattern
        
    def _finishBlock(self, outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName):
        if prevParsedIdx != firstParsedIdx:
            outLines.append('    for {} = {}, {} {{'.format(idxVarName, firstParsedIdx, prevParsedIdx))
            outLines.append('    ' + prevParsedPattern)
            outLines.append('    }')
            return True
        else:
            outLines.append(prevLine)
            return False
        
    def _wrapInnerCycles(self, lines):
        outLines = []
        
        isInsideBlock = False
        linesBlock = []
        for line in lines:
            if ' for ' in line:
                isInsideBlock = True
                linesBlock.append(line)
            elif ' }' in line:
                linesBlock.append(line)
                outLines.append('\n'.join(linesBlock))
                isInsideBlock = False
                linesBlock = []
            elif isInsideBlock:
                linesBlock.append(line)
            else:
                outLines.append(line)
                
        if isInsideBlock:
            codeContractViolation()
            
        return outLines
        
    def _unwrapInnerCycles(self, lines):
        outLines = []
        for line in lines:
            if '\n' in line:
                newLines = line.split('\n')
                outLines.append(newLines[0])
                newLines = ['    ' + newLine for newLine in newLines[1 :]]
                outLines.extend(newLines)
            else:
                outLines.append(line)
        return outLines
        
    def _rfindExt(self, line, marker, isSecondIteration):
        idx = line.rfind(marker)
        if idx == -1:
            return idx
        if isSecondIteration:
            idx = line.rfind(marker, 0, idx)
        return idx
        
    def _getTemplateName(self, hocTemplInst):
        templName = str(hocTemplInst)
        idx = templName.index('[')
        templName = templName[: idx]
        return templName
        
    def _linesOrEmptyParagraphHint(self, lines):
        if len(lines) != 0:
            return lines
        else:
            return emptyParagraphHint()
            
    def _exportSomeFilesFromThisDir(self, lines, relDirPath, idxs, idxToFileNameDict):
        isFirstDistFunc = True
        for idx in sorted(idxs):
            if not isFirstDistFunc:
                lines.append('')
            fileName = idxToFileNameDict[idx]
            relFilePathName = relDirPath + '\\' + fileName
            newLines = self.insertAllLinesFromFile(relFilePathName)
            lines.extend(newLines)
            lines.append('')
            isFirstDistFunc = False
            