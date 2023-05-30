
import os
from neuron import h, hoc, nrn
from Generators.GenForMechComps import *
from Generators.GensForHomogenVars import *
from Generators.GensForInhomAndStochModels import *
from OtherUtils import *


class Generators:
    
    _defaultNseg = 1
    _defaultRa = 35.4
    
    _hocObj = hoc.HocObject()
    _genForMechComps = GenForMechComps()

    # Other data members that will be added in the ctor (they all depend on hoc:ExportOptions, so we defer the construction):
    #   _exportOptions
    #   _gensForHomogenVars
    #   _gensForInhomAndStochModels
    
    def __init__(self):
        self._exportOptions = self._hocObj.exportOptions
        self._gensForHomogenVars = GensForHomogenVars()
        self._gensForInhomAndStochModels = GensForInhomAndStochModels()
        
    def getUtils(self):
        lines = []
        
        lines.append('objref nil')
        lines.append('')
        
        for fileName in ['InterModularErrWarnUtils_Exported.hoc', 'InterModularListUtils_Exported.hoc', 'InterModularStringUtils_Exported.hoc', 'InterModularOtherUtils_Exported.hoc']:
            newLines = self.insertAllLinesFromFile('Code\\InterModular\\Exported\\' + fileName)
            lines.extend(newLines)
            lines.append('')
        
        # The instances of the next reduced templates from "InterModular" folder are created
        # only in standalone mode; otherwise we just reuse the instances created earlier in the main program
        
        newLines = self.insertAllLinesFromReducedVersionFile('InterModular\\ReducedBasicMath.hoc')
        lines.extend(newLines)
        lines.append('')
        
        if self._exportOptions.isExportAnyStochFuncs():
            lines.append('')
            newLines = self.insertAllLinesFromReducedVersionFile('InterModular\\ReducedRNGUtils.hoc')
            lines.extend(newLines)
            
        return lines
        
    def checkPrerequisites(self):
        if not self._exportOptions.isPythonRequired():
            return emptyParagraphHint()
            
        lines = []
        
        lines.append('if (!nrnpython("")) {')
        lines.append('    printMsgAndRaiseError("Sorry, this HOC file requires Python for some operations. Please install Python.")')
        lines.append('}')
        lines.append('')
        lines.append('objref pyObj')
        lines.append('pyObj = new PythonObject()')
        
        if self._exportOptions.isExportSyns:
            lines.append('')
            newLines = self.insertAllLinesFromFile('Code\\InterModular\\Exported\\InterModularPythonUtils_Exported.hoc')
            lines.extend(newLines)
            
        return lines
        
    def getAllCreateStatementsExceptNanogeometry(self):
        # output: a string like 'create name1, name2[123], name3[456][7], ...'
        
        # Get all names (base geometry, nanogeometry, extracellular source etc.)
        # !! it's not optimal because:
        # (1) there is a lot of nanogeometry sections with known names (no need to use slow "forall")
        # (2) we already had all base geometry names at some point before (in Import module)
        allNames = self._hocObj.getAllSectionNames()    # !! for nanogeometry it simply returns AstrocyteNanoBranch, but the full name is AstrocyteNanoBranch[1].LargeGlia[2]
        
        if len(allNames) == 0:
            codeContractViolation()
        
        createdNames = []
        for name in allNames:
            createdName = name.s
            
            # !! update this logic once I correct/replace obfunc getAllSectionNames which produces allNames
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
                    'for idx = 0, {} {{'.format(len(secObj) - 1),
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
    # !! investigate at which stage of the program the 3D-coordinates of 1st point of 1st imported dendrite become changed (at least in the next files: AstrocyteBasicGeometry.hoc and cellmorphology.hoc)
    #    "connect" command does not change them, so maybe "finitialize"?
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
        
    def createImportabilityMeasures(self):
        
        lines = []
        
        # Check whether we are in "start with nano" mode or "standalone" mode
        lines.append('isLoadedFromMainProgram = 1')
        lines.append('{ makeSureDeclared("isBaseOrNanoStart", "isLoadedFromMainProgram = 0") }')
        lines.append('')
        
        # Make sure "nrnmech.dll" is loaded and valid
        if self._exportOptions.isExportDistMechs or self._exportOptions.isExportSyns:
            lines.append('{ makeSureDeclared("ifMissingInThisFolderThenLoadDefaultMechsDllDependingOnCellType", "proc %s() { codeContractViolation() }") }')
            lines.append('objref mechType')
            lines.append('if (isLoadedFromMainProgram) {')
            lines.append('    ifMissingInThisFolderThenLoadDefaultMechsDllDependingOnCellType()')
            lines.append('} else {')
            if self._exportOptions.isExportDistMechs:
                newLines = self._createCheckForNumMechs(0, 'Distributed Membrane Mechanisms')
                lines.extend(newLines)
            if self._exportOptions.isExportSyns:
                newLines = self._createCheckForNumMechs(1, 'Point Processes')
                lines.extend(newLines)
            lines.append('}')
            lines.append('')
            
        # Make sure the staff from ReducedVersions\InterModular is either:
        #   preserved ("start with nano" mode)
        #   created ("standalone" mode with real usage)
        #   declared as nil ("standalone" mode without real usage)
        
        lines.append('{ makeSureDeclared("math", "objref %s", "%s = new ReducedBasicMath()") }')
        
        if self._exportOptions.isExportAnyStochFuncs():
            # !!!! BUG: The random sequences won't be the same in the main program and the exported file until
            #      each seed given by rngUtils.getFor_stochFunc_withUniqueSeed is saved into corresponding stocDistFunc
            #      and exported/imported as a part of it
            lines.append('{ makeSureDeclared("rngUtils", "objref %s", "%s = new ReducedRNGUtils()") }')
            lines.append('')
        elif self._exportOptions.isExportSyns or self._exportOptions.isExportInhomAndStochLibrary():
            lines.append('{ makeSureDeclared("rngUtils") }')
            lines.append('')
            
        # Make sure all the required objref-s are declared as nil
        names = []
        names.append('mmAllComps')
        if self._exportOptions.isExportSyns or self._exportOptions.isExportInhomAndStochLibrary():
            names.append('smAllComps')
            names.append('smAllSyns')
            names.append('seh')
        line = 'objref ' + ', '.join(names)
        lines.append(line)
        
        return lines
        
    def createInhomAndStochLibrary(self):
        if not self._exportOptions.isExportInhomAndStochLibrary():
            return emptyParagraphHint()
            
        lines = []
        
        # !! try to avoid exporting the RNG staff in ReducedInhomAndStochTarget if not self._exportOptions.isExportAnyStochFuncs()
        newLines = self.insertAllLinesFromReducedVersionFile('ReducedInhomAndStochTarget.hoc')
        lines.extend(newLines)
        lines.append('')
        
        newLines = self.insertAllLinesFromReducedVersionFile('ReducedInhomAndStochLibrary.hoc')
        lines.extend(newLines)
        lines.append('')
        
        if self._exportOptions.isExportAnyStochFuncs():
            newLines = self.insertAllLinesFromFile('Code\\Managers\\InhomAndStochLibrary\\Exported\\InhomAndStochApplicator.hoc')
            lines.extend(newLines)
            lines.append('')
            
        lines.append('objref vecOfVals, listOfStrs')
        
        return lines
        
    # !! some code dupl. with insertAllUsedStochFuncs
    def insertAllUsedDistFuncs(self):
        if not self._exportOptions.isExportAnyDistFuncs():
            return emptyParagraphHint()
            
        lines = []
        
        dfhTemplNames = set()
        isTablePlusLinInterpDistFuncExported = False
        for actSpecVar in h.inhomAndStochLibrary.activeSpecVars:
            if not self._exportOptions.isExportedInhomVar(actSpecVar):
                continue
            dfhTemplNames.add(getTemplateName(actSpecVar.distFuncHelper))
            if actSpecVar.distFuncCatIdx == self._hocObj.dfc.tablePlusLinInterpDistFuncCatIdx:
                isTablePlusLinInterpDistFuncExported = True
            
        if isTablePlusLinInterpDistFuncExported:
            # !! just a temp solution: to get rid of this, we need to split TablePlusLinInterpDistFuncHelper template into two:
            #    table from TextEditor/Vector-s and table from file (only the first one will be exported)
            lines.append('makeSureDeclared("mwh")')
            lines.append('')
            lines.append('func selectDistFuncInputFile() { codeContractViolation() }')
            lines.append('')
        
        relDirPath = 'Code\\Managers\\InhomAndStochLibrary\\InhomModels\\DistFuncHelpers\\Exported'
        self._exportTheseTemplatesFromThisDir(lines, relDirPath, dfhTemplNames)
        lines.append('')
        
        if self._exportOptions.isExportSegmentationHelper():
            newLines = self.insertAllLinesFromReducedVersionFile('ReducedSegmentationHelper.hoc')
            lines.extend(newLines)
            lines.append('')
            
        lines.append('objref segmentationHelper, distFuncHelper')
        
        return lines
        
    # !! some code dupl. with insertAllUsedDistFuncs
    def insertAllUsedStochFuncs(self):
        if not self._exportOptions.isExportAnyStochFuncs():
            return emptyParagraphHint()
            
        lines = []
        
        # !!! just a temp solution: we need to bind these names as templates' external-s even though
        #     they won't be used (because we don't call all the methods in the exported file);
        #     at the same time, when the file is loaded from the main program, the file needs to:
        #     (1) preserve all already created "InterModular" objects and callables (e.g. "mwh" and "eachPointInGrid")
        #     (2) stub all required objects and callables allowing them to be defined later in the main program (e.g. "specMath" and "callPythonFunction")
        lines.append('{ makeSureDeclared("mwh") }')
        lines.append('{ makeSureDeclared("stochTestGraph") }')
        lines.append('{ makeSureDeclared("eachPointInGrid", "iterator %s() { codeContractViolation() }") }')
        lines.append('objref specMath')
        lines.append('func callPythonFunction() { codeContractViolation() }')
        lines.append('proc definePythonFunction() { codeContractViolation() }')
        lines.append('func loadPythonFile() { codeContractViolation() }')
        lines.append('func selectDistFuncInputFile() { codeContractViolation() }')
        lines.append('')
        
        sdhTemplNames = set()
        sfhTemplNames = set()
        for actSpecVar in h.inhomAndStochLibrary.activeSpecVars:
            if not self._exportOptions.isExportedStochVar(actSpecVar):
                continue
            stochFuncHelper = actSpecVar.stochFuncHelper
            if actSpecVar.stochFuncCatIdx == self._hocObj.sfc.simpleModelStochFuncCatIdx:
                sdhTemplNames.add(getTemplateName(stochFuncHelper.distHelper))
            sfhTemplNames.add(getTemplateName(stochFuncHelper))
            
        relDirPath = 'Code\\Managers\\InhomAndStochLibrary\\StochModels\\StochDistHelpers\\Exported'
        self._exportTheseTemplatesFromThisDir(lines, relDirPath, sdhTemplNames)
        
        relDirPath = 'Code\\Managers\\InhomAndStochLibrary\\StochModels\\StochFuncHelpers\\Exported'
        self._exportTheseTemplatesFromThisDir(lines, relDirPath, sfhTemplNames)
        
        newLines = self.insertAllLinesFromFile('Code\\Managers\\Widgets\\Stochasticity\\Exported\\ColourizationHelper.hoc')
        lines.extend(newLines)
        lines.append('')
        
        newLines = self.insertAllLinesFromFile('Code\\Managers\\Widgets\\Stochasticity\\Exported\\BoundingHelper.hoc')
        lines.extend(newLines)
        lines.append('')
        
        lines.append('objref colourizationHelper, boundingHelper, stochFuncHelper')
        
        return lines
        
    def createReducedMechComps(self):
    
        lines = []
        
        if not self._exportOptions.isExportDistMechs:
            fileName = 'ReducedMechComp1.hoc'   # name, list_ref
        else:
            fileName = 'ReducedMechComp2.hoc'   # name, list_ref, isMechInserted, mechStds
        newLines = self.insertAllLinesFromReducedVersionFile(fileName)
        lines.extend(newLines)
        lines.append('')
        
        newLines = self._genForMechComps.createReducedMechComps()
        lines.extend(newLines)
        
        return lines
        
    def initHomogenBiophysics(self):
        return self._gensForHomogenVars.initHomogenBiophysics()
        
    def createInhomBiophysModels(self):
        return self._gensForInhomAndStochModels.createInhomBiophysModels()
        
    def createStochBiophysModels(self):
        return self._gensForInhomAndStochModels.createStochBiophysModels()
        
    # Keep in sync with hoc:createSynComps
    def createReducedSynComps(self):
        if not self._exportOptions.isExportSyns:
            return emptyParagraphHint()
            
        lines = self.insertAllLinesFromFile('Code\\Managers\\SynManager\\Exported\\EnumSynCompIdxs.hoc')
        lines.append('')
        
        newLines = self.insertAllLinesFromReducedVersionFile('ReducedSynPPComp.hoc')
        lines.extend(newLines)
        lines.append('')
        
        synGroup = self._hocObj.synGroup
        is3Or1PartInSynStruc = synGroup.is3Or1PartInSynStruc()
        
        # Note: NEURON doesn't allow appending "nil" to a List, so we don't skip exporting this template if !is3Or1PartInSynStruc
        newLines = self.insertAllLinesFromReducedVersionFile('ReducedSynNCComp.hoc')
        lines.extend(newLines)
        lines.append('')
        
        if is3Or1PartInSynStruc:
            newLines = self.insertAllLinesFromReducedVersionFile('ReducedMechTypeHelper.hoc')
            lines.extend(newLines)
            lines.append('')
        
        if self._exportOptions.isExportSynEventsHelper() or is3Or1PartInSynStruc:
            newLines = self.insertAllLinesFromReducedVersionFile('ReducedManagersCommonUtils.hoc')
            lines.extend(newLines)
            lines.append('')
            
            newLines = self.insertAllLinesFromFile('Code\\Managers\\SynManager\\Exported\\SynEventsHelper.hoc')
            lines.extend(newLines)
            lines.append('')
            
        if is3Or1PartInSynStruc:
            newLines = self.insertAllLinesFromFile('Code\\Managers\\SynManager\\FakesForNetCon\\Exported\\UtilsForFakeMechanismForNetCon.hoc')
            lines.extend(newLines)
            lines.append('')
            
            newLines = self.insertAllLinesFromFile('Code\\Managers\\SynManager\\FakesForNetCon\\Exported\\FakeMechanismStandardForNetCon.hoc')
            lines.extend(newLines)
            lines.append('')
            
        newLines = self.insertAllLinesFromReducedVersionFile('ReducedSynGroup.hoc')
        lines.extend(newLines)
        lines.append('')
        
        lines.append('smAllComps = new List()')
        lines.append('')
        
        srcMechIdx = int(synGroup.getMechIdxAndOptionalName(0))
        trgMechIdx = int(synGroup.getMechIdxAndOptionalName(1))
        sngMechIdx = int(synGroup.getMechIdxAndOptionalName(2))
        
        # Keep in sync with hoc:EnumSynCompIdxs.init, hoc:createOrImportSynComps and py:initHomogenSynVars
        # Note: NEURON doesn't allow appending "nil" to a List, so we don't optimize this depending on is3Or1PartInSynStruc
        lines.append('{{ smAllComps.append(new ReducedSynPPComp("Source PP", 0, {})) }}'.format(srcMechIdx))
        lines.append('{ smAllComps.append(new ReducedSynNCComp()) }')
        lines.append('{{ smAllComps.append(new ReducedSynPPComp("Target PP", 1, {})) }}'.format(trgMechIdx))
        lines.append('{{ smAllComps.append(new ReducedSynPPComp("Single PP", 2, {})) }}'.format(sngMechIdx))
        
        return lines
        
    def initHomogenSynVars(self):
        return self._gensForHomogenVars.initHomogenSynVars()
        
    def createInhomSynModels(self):
        return self._gensForInhomAndStochModels.createInhomSynModels()
        
    def createStochSynModels(self):
        return self._gensForInhomAndStochModels.createStochSynModels()
        
    def createSynEpilogue(self):
        if not self._exportOptions.isExportSyns:
            return emptyParagraphHint()
            
        lines = []
        
        lines.append('// !! synGroup.applyChangesToLoc(*)')
        
        synGroup = self._hocObj.synGroup
        is3Or1PartInSynStruc = int(synGroup.is3Or1PartInSynStruc())
        srcMechName = h.ref('')
        trgMechName = h.ref('')
        sngMechName = h.ref('')
        srcMechIdx = int(synGroup.getMechIdxAndOptionalName(0, srcMechName))
        trgMechIdx = int(synGroup.getMechIdxAndOptionalName(1, trgMechName))
        sngMechIdx = int(synGroup.getMechIdxAndOptionalName(2, sngMechName))
        srcMechName = srcMechName[0]
        trgMechName = trgMechName[0]
        sngMechName = sngMechName[0]
        isForceNewTrgOrSng = 1  # !!!!??
        lines.append('{{ synGroup.applyChangesToStrucIfNeeded({}, {}, {}, {}, "{}", "{}", "{}", {}) }}'.format(is3Or1PartInSynStruc, srcMechIdx, trgMechIdx, sngMechIdx, srcMechName, trgMechName, sngMechName, isForceNewTrgOrSng))
        
        lines.append('// !! synGroup.applyChangesToDirtyHomogenVars(*)')
        
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
        lines.append('{ altRunControlWidget.show() }')
        
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
        
    def getListOfStringsFromTopLevel(self, varName):
        lines = []
        lines.append('objref {}'.format(varName))
        lines.append('{} = new List()'.format(varName))
        listOfStrs = self._getHocVar(varName)
        for thisStr in listOfStrs:
            lines.append('{{ {}.append(new String("{}")) }}'.format(varName, thisStr.s))
        return lines
        
        
    def _createCheckForNumMechs(self, isDmOrPp, hint):
        lines = []
        lines.append('    mechType = new MechanismType({})     // {}: "{}"'.format(isDmOrPp, isDmOrPp, hint))
        lines.append('    if (mechType.count() != {}) {{'.format(int(self._hocObj.mth.getNumMechs(isDmOrPp))))
        lines.append('        printMsgAndRaiseError("Please make sure the correct file \\"nrnmech.dll\\" is present in the same folder with this HOC file.")')
        lines.append('    }')
        return lines
        
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
            
    def _exportTheseTemplatesFromThisDir(self, lines, relDirPath, templNames):
        isFirstTemplate = True
        for templName in templNames:
            if not isFirstTemplate:
                lines.append('')
            relFilePathName = relDirPath + '\\' + templName + '.hoc'
            newLines = self.insertAllLinesFromFile(relFilePathName)
            lines.extend(newLines)
            lines.append('')
            isFirstTemplate = False
            