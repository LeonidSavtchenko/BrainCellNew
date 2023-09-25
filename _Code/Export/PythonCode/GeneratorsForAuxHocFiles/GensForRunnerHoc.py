
from Utils.UnitsUtils import UnitsUtils
from Utils.OtherUtils import *


class GensForRunnerHoc:
    
    # Data member that will be added in the ctor:
    #   _outMainHocFileName
    
    def __init__(self, outMainHocFileName):
        self._outMainHocFileName = outMainHocFileName
        
    def getRunnedHocFileName(self):
        lines = []
        
        lines.append('strdef runnedHocFileName')
        lines.append('runnedHocFileName = "{}"'.format(self._outMainHocFileName))
        
        return lines
        
    def getOutFolderAndFileNames(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isAnyWatchedVars or isAnyWatchedAPCounts):
            return emptyParagraphHint()
            
        lines = []
        
        varNames = []
        varNames.append('outBaseFolder')
        if isRepeatForStats:
            varNames.append('outSubFolderNameFormat')
        if isAnyWatchedVars:
            varNames.append('outVarsFileNameFormat')
        if isAnyWatchedAPCounts:
            varNames.append('outAPsFileNameFormat')
        varNames.append('outFileNameTimestampFormat')
        if isAnyWatchedAPCounts:
            if isAnySweptVars:
                varNames.append('outAPsSweepSummaryFileName')
            if isRepeatForStats:
                varNames.append('outAPsRepSummaryFileName')
        lines.append('strdef ' + ', '.join(varNames))
        
        lines.append('outBaseFolder = "results"   // This can be either a folder name, an absolute path or a relative path (use "/" and avoid Unicode)')
        if isRepeatForStats:
            lines.append('outSubFolderNameFormat = "repetition %d"')
        if isAnyWatchedVars:
            lines.append('outVarsFileNameFormat = "vars %s.txt"')
        if isAnyWatchedAPCounts:
            lines.append('outAPsFileNameFormat = "aps %s.txt"')
        lines.append('outFileNameTimestampFormat = "%Y-%m-%d %H.%M.%S"')
        if isAnyWatchedAPCounts:
            if isAnySweptVars:
                lines.append('outAPsSweepSummaryFileName = "aps sweep summary.txt"')
            if isRepeatForStats:
                lines.append('outAPsRepSummaryFileName = "aps repetition summary.txt"')
            
        return lines
        
    def getSweptVarsAndRepetitionSettings(self):
        if not (hocObj.exportOptions.isAnySweptVars() or hocObj.exportOptions.isRepeatForStats):
            return emptyParagraphHint()
            
        lines = []
        
        if hocObj.exportOptions.isAnySweptVars():
            sweptVarsList = hocObj.exportOptions.sweptVarsList
            numSweptVars = len(sweptVarsList)
            
            if hocObj.exportOptions.isAnyWatchedVars() or hocObj.exportOptions.isAnyWatchedAPCounts():
                lines.append('objref sweptVarUserReadableNames')
                lines.append('sweptVarUserReadableNames = new List()')
                for sweptVar in sweptVarsList:
                    userReadableName = sweptVar.s.replace('\\', '\\\\')
                    lines.append(f'{{ sweptVarUserReadableNames.append(new String("{userReadableName}")) }}')
                lines.append('')
                
                lines.append('objref sweptVarUnits')
                lines.append('sweptVarUnits = new List()')
                for sweptVar in sweptVarsList:
                    units = UnitsUtils.getUnitsForSweptVar(sweptVar)
                    lines.append(f'{{ sweptVarUnits.append(new String("{units}")) }}')
                lines.append('')
                
            for sweptVarIdx in range(numSweptVars):
                sweptVar = sweptVarsList[sweptVarIdx]
                unitsCommentOrEmpty = UnitsUtils.getUnitsCommentOrEmptyForExposedOrSweptVar1(sweptVar)
                lines.append(f'// {sweptVar.s}{unitsCommentOrEmpty}')
                gridInfoOrNil = sweptVar.gridInfoOrNil
                if gridInfoOrNil is not None:
                    gridSize = int(gridInfoOrNil.numPts)
                else:
                    gridSize = 1
                lines.append(f'sweptVar{sweptVarIdx + 1}GridSize = {gridSize}')
                lines.append(f'double sweptVar{sweptVarIdx + 1}Grid[sweptVar{sweptVarIdx + 1}GridSize]')
                if gridInfoOrNil is not None:
                    for ptIdx in range(gridSize):
                        lines.append(f'sweptVar{sweptVarIdx + 1}Grid[{ptIdx}] = {gridInfoOrNil.getValue(ptIdx)}')
                else:
                    lines.append(f'sweptVar{sweptVarIdx + 1}Grid[0] = {sweptVar.getValue()}')
                lines.append('')
                
        if hocObj.exportOptions.isRepeatForStats:
            lines.append(f'numRepeatsForStats = {int(hocObj.exportOptions.numRepeatsForStats)}')
            lines.append('')
            
        if hocObj.exportOptions.isAnySweptVars():
            totalNumSimsExpr = ' * '.join(f'sweptVar{sweptVarIdx + 1}GridSize' for sweptVarIdx in range(numSweptVars))
            if hocObj.exportOptions.isRepeatForStats:
                totalNumSimsExpr = 'numRepeatsForStats * ' + totalNumSimsExpr
        else:
            totalNumSimsExpr = 'numRepeatsForStats'
        lastLine = 'totalNumSims = ' + totalNumSimsExpr
        
        lines.append(lastLine)
        
        return lines
        
    def getWatchedVarsAndRecorderSettings(self):
        if not (hocObj.exportOptions.isAnyWatchedVars() or hocObj.exportOptions.isAnyWatchedAPCounts()):
            return emptyParagraphHint()
            
        lines = []
        
        if hocObj.exportOptions.isAnyWatchedVars():
            watchedVarsList = hocObj.exportOptions.watchedVarsList
            
            lines.append('objref watchedVarNames')
            lines.append('watchedVarNames = new List()')
            for watchedVar in watchedVarsList:
                lines.append('{{ watchedVarNames.append(new String("{}")) }}'.format(watchedVar.s))
            lines.append('')
            
            lines.append('objref watchedVarUnits')
            lines.append('watchedVarUnits = new List()')
            for watchedVar in watchedVarsList:
                units = UnitsUtils.getUnitsForWatchedVar(watchedVar.s)
                lines.append('{{ watchedVarUnits.append(new String("{}")) }}'.format(units))
            lines.append('')
            
            lines.append('// Recording period (in model time, optional)')
            if hocObj.exportOptions.DtOrMinus1 != -1:
                units = UnitsUtils.getUnitsForWatchedVar('dt')
                lines.append('DtOrMinus1 = {}    // ({})'.format(hocObj.exportOptions.DtOrMinus1, units))
            else:
                lines.append('DtOrMinus1 = {}'.format(int(hocObj.exportOptions.DtOrMinus1)))
            lines.append('')
            
        lines.append('strdef oneValueFormat, colSep')
        lines.append('')
        lines.append('// Format hints:')
        lines.append('//  "%g"     - mid precision, jagged columns (compact format)')
        lines.append('//  "%.15e"  - max precision, fixed column width (with exponent)')
        lines.append('//  "%-8.4g" - low precision, fixed column width (left alignment)')
        lines.append('//  "%8.4g"  - low precision, fixed column width (right alignment)')
        lines.append('//  "%.15g"  - max precision, jagged columns (compact format, without ".0")')
        lines.append('//  "@py"    - max precision, jagged columns (compact format, with ".0")')
        lines.append('oneValueFormat = "%-8.4g"')
        lines.append('')
        lines.append(r'colSep = "\t"   // Origin imports fine with ";" or "," as well')
        
        return lines
        
    def getUtilsPrologue(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isAnySweptVars or isRepeatForStats or isAnyWatchedVars or isAnyWatchedAPCounts):
            return emptyParagraphHint()
            
        lines = getAllLinesFromFile('_Code\\InterModular\\Exported\\InterModularErrWarnUtilsPart1_Exported.hoc')
        return lines
        
    def checkPrerequisites(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isAnySweptVars or isRepeatForStats or isAnyWatchedVars or isAnyWatchedAPCounts):
            return emptyParagraphHint()
            
        lines = getAllLinesFromFile('_Code\\Export\\OutHocFileStructures\\PythonCheck.hoc')
        
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append('')
            newLines = getAllLinesFromFile('_Code\\Export\\OutHocFileStructures\\RunnerHocUtils\\RunnerHocWatchedVarsPrereqs.hoc')
            lines.extend(newLines)
            
        return lines
        
    def getFileInfrastructureUtils(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isAnySweptVars or isRepeatForStats or isAnyWatchedVars or isAnyWatchedAPCounts):
            return emptyParagraphHint()
            
        lines = []
        
        if isAnySweptVars or isRepeatForStats:
            newLines = self._insertAllLinesFromRunnerHocUtilsFile('RunnerHocTempUtils.hoc')
            lines.extend(newLines)
        else:
            lines.append('strdef tempFolderName, tempHocFilePathName')
            
        if (isAnyWatchedVars or isAnyWatchedAPCounts) and isRepeatForStats:
            lines.append('')
            lines.append('strdef outFolderPathNameFormat')
            lines.append('{ sprint(outFolderPathNameFormat, "%s/%s", outBaseFolder, outSubFolderNameFormat) }')
            
        lines.append('')
        newLines = self._insertAllLinesFromRunnerHocUtilsFile('RunnerHocCreateUtils.hoc')
        lines.extend(newLines)
        
        if isAnySweptVars or isRepeatForStats:
            lines.append('')
            newLines = self._insertAllLinesFromRunnerHocUtilsFile('RunnerHocDeleteUtils.hoc')
            lines.extend(newLines)
            
        return lines
        
    def getRecordingUtils(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isAnyWatchedVars or isAnyWatchedAPCounts):
            return emptyParagraphHint()
            
        lines = self._insertAllLinesFromRunnerHocUtilsFile('RunnerHocWatchedUtils.hoc')
        
        lines.append('')
        if isAnySweptVars:
            lines.append('numSweptVars = sweptVarUserReadableNames.count()')
        else:
            lines.append('numSweptVars = 0')
            
        if isAnyWatchedVars:
            lines.append('')
            newLines = self._insertAllLinesFromRunnerHocUtilsFile('RunnerHocWatchedVarsUtils.hoc')
            lines.extend(newLines)
            
        if isAnyWatchedAPCounts:
            lines.append('')
            newLines = self._insertAllLinesFromRunnerHocUtilsFile('RunnerHocWatchedAPCountsUtils.hoc')
            lines.extend(newLines)
            
        if isAnySweptVars:
            lines.append('')
            newLines = self._insertAllLinesFromRunnerHocUtilsFile('RunnerHocSweepAndWatchUtils.hoc')
            lines.extend(newLines)
            
        return lines
        
    def getAPCountsSweepSummaryFileUtils(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isAnySweptVars and isAnyWatchedAPCounts):
            return emptyParagraphHint()
            
        lines = self._insertAllLinesFromRunnerHocUtilsFile('RunnerHocSweepAndWatchAPCountsUtils.hoc')
        
        return lines
        
    def getAPCountsRepetitionSummaryFileUtils(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isRepeatForStats and isAnyWatchedAPCounts):
            return emptyParagraphHint()
            
        lines = []
        
        sweptVarsList = hocObj.exportOptions.sweptVarsList
        numSweptVars = len(sweptVarsList)
        
        if isAnySweptVars:
            allOneSweptVarDims = '[1]' * numSweptVars
            sweptVarIdxs = '[sweptVar' + 'Idx][sweptVar'.join(str(idx + 1) for idx in range(numSweptVars)) + 'Idx]'
        else:
            allOneSweptVarDims = ''
            sweptVarIdxs = ''
            
        lines.append('// Just declarations for binding, will be re-defined with proper sizes later')
        lines.append(f'double minNumSpikes{allOneSweptVarDims}[1]')
        lines.append(f'double maxNumSpikes{allOneSweptVarDims}[1]')
        lines.append(f'double sumNumSpikes{allOneSweptVarDims}[1]')
        lines.append('')
        lines.append('// in: sweptVar*Idx (taken from the top level)')
        lines.append('proc getMinMaxSumNumSpikes() { local apcIdx')
        lines.append('    apcIdx = $1')
        lines.append(f'    $&2 = minNumSpikes{sweptVarIdxs}[apcIdx]')
        lines.append(f'    $&3 = maxNumSpikes{sweptVarIdxs}[apcIdx]')
        lines.append(f'    $&4 = sumNumSpikes{sweptVarIdxs}[apcIdx]')
        lines.append('}')
        lines.append('')
        lines.append('// in: sweptVar*Idx (taken from the top level)')
        lines.append('proc updateDataForAPCountsRepSummaryFile() { local apcIdx, n')
        lines.append('    for apcIdx = 0, numWatchedAPCounts - 1 {')
        lines.append('        n = APCount[apcIdx].n')
        lines.append(f'        if (minNumSpikes{sweptVarIdxs}[apcIdx] == 0 || minNumSpikes{sweptVarIdxs}[apcIdx] > n) {{')
        lines.append(f'            minNumSpikes{sweptVarIdxs}[apcIdx] = n')
        lines.append('        }')
        lines.append(f'        if (maxNumSpikes{sweptVarIdxs}[apcIdx] < n) {{')
        lines.append(f'            maxNumSpikes{sweptVarIdxs}[apcIdx] = n')
        lines.append('        }')
        lines.append(f'        sumNumSpikes{sweptVarIdxs}[apcIdx] += n')
        lines.append('    }')
        lines.append('}')
        lines.append('')
        lines.append('// in: sweptVar*GridSize, sweptVar*Grid (taken from the top level)')
        lines.append('proc saveAPCountsRepSummaryFile() { localobj outFile')
        lines.append('    outFile = createAPCountsRepSummaryFileWithHeaders()')
        if isAnySweptVars:
            indent = self._openSweptVarCycles(lines, sweptVarsList, stdIndent)
        else:
            indent = stdIndent
        lines.append(indent + 'appendOneDataRowToAPCountsRepSummaryFile(outFile)')
        if isAnySweptVars:
            self._closeSweptVarCycles(lines, numSweptVars, indent)
        lines.append('    outFile.close()')
        lines.append('}')
        
        if not isAnySweptVars:
            lines.append('')
            lines.append('strdef _sweptVarName')
            lines.append('objref sweptVarUnits, sweptVarUserReadableNames')
            
        lines.append('')
        newLines = self._insertAllLinesFromRunnerHocUtilsFile('RunnerHocRepeatAndWatchAPCountsUtils.hoc')
        lines.extend(newLines)
        
        return lines
        
    def getMainPart(self):
        lines = []
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        isExportAltRunControl = hocObj.exportOptions.isExportAltRunControl()
        
        if isAnySweptVars:
            sweptVarsList = hocObj.exportOptions.sweptVarsList
        else:
            sweptVarsList = []
        numSweptVars = len(sweptVarsList)
        
        isCreateTempHocFileWithoutTemplates = (isAnySweptVars or isRepeatForStats)
        isCreateOrCleanUpOutFolder = (isAnyWatchedVars or isAnyWatchedAPCounts)
        if isCreateOrCleanUpOutFolder:
            lines.append('outFolderPathName = outBaseFolder')
        if isCreateTempHocFileWithoutTemplates or isCreateOrCleanUpOutFolder:
            lines.append('createTempHocFileWithoutTemplatesAndOutputFolder("{}", "{}")'.format(bool(isCreateTempHocFileWithoutTemplates), bool(isCreateOrCleanUpOutFolder)))
            lines.append('')
            
        if isAnySweptVars or isRepeatForStats:
            lines.append(r'print "\nIf you need to break the cycle by simulations, just Stop the current simulation.\n"')
            lines.append('')
            
        if isExportAltRunControl:
            if isAnySweptVars or isRepeatForStats:
                lines.append('objref altRunControlWidget')
                lines.append('')
            if isAnySweptVars and isRepeatForStats:
                lines.append('uniqueSeedForHoc = -1')
                lines.append('uniqueSeedForMod = -1')
                lines.append('')
        else:
            lines.append('nrncontrolmenu()')
            lines.append('')
            
        if isAnySweptVars or isRepeatForStats:
            lines.append('simIdx = 1')
            lines.append('')
            
        if isRepeatForStats:
            lines.append('for repIdx = 1, numRepeatsForStats {')
            indent = stdIndent
            if isAnyWatchedVars or isAnyWatchedAPCounts:
                lines.append(indent + 'sprint(outFolderPathName, outFolderPathNameFormat, repIdx)')
                lines.append(indent + 'createTempHocFileWithoutTemplatesAndOutputFolder("False", "True")')
            lines.append(indent)
        else:
            indent = ''
            
        if isAnySweptVars:
            if isRepeatForStats and (isExportAltRunControl or isAnyWatchedAPCounts):
                lines.append(indent + 'if (repIdx != 1) {')
                indent1 = indent + stdIndent
                if isExportAltRunControl:
                    # Avoiding "object prefix is NULL", we use "execute" here instead of "objref rngUtils" upstream
                    # because we'll call makeSureDeclared("rngUtils") downstream and need to have the object NOT declared
                    lines.append(indent1 + 'execute("rngUtils.getAllSeeds(&uniqueSeedForHoc, &uniqueSeedForMod)")')
                if isAnyWatchedAPCounts:
                    lines.append(indent1 + 'createAPCountsSweepSummaryFileWithHeaders()')
                lines.append(indent + '}')
                lines.append(indent)
                
            indent = self._openSweptVarCycles(lines, sweptVarsList, indent)
            
        if isAnySweptVars or isRepeatForStats:
            lines.append(indent + r'printf("Running simulation %d of %d ...\n", simIdx, totalNumSims)')
        else:
            lines.append(indent + r'{ printf("\nRunning simulation ...\n") }')
        lines.append(indent)
        
        indent2 = indent + stdIndent
        
        if not (isAnySweptVars or isRepeatForStats):
            lines.append(indent + '{ load_file(runnedHocFileName) }')
            indent3 = indent
        else:
            lines.append(indent + 'if (simIdx == 1) {')
            lines.append(indent2 + 'load_file(runnedHocFileName)')
            indent3 = indent2
            
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append(indent3)
            lines.append(indent3 + 'checkCVodePrerequisites()')
            
        if isAnyWatchedAPCounts:
            lines.append(indent3)
            lines.append(indent3 + 'apcList = new List("APCount")')
            lines.append(indent3 + 'numWatchedAPCounts = apcList.count()')
            lines.append(indent3 + 'objref recordedVecsFromAPCounts[numWatchedAPCounts]')
            
            if isAnySweptVars:
                lines.append(indent3)
                # !! would it make sense to do this later when we record the first data row?
                lines.append(indent3 + 'createAPCountsSweepSummaryFileWithHeaders()')
                
            if isRepeatForStats:
                lines.append(indent3)
                if isAnySweptVars:
                    sweptVarDims = '[sweptVar' + 'GridSize][sweptVar'.join(str(idx + 1) for idx in range(numSweptVars)) + 'GridSize]'
                else:
                    sweptVarDims = ''
                lines.append(indent3 + f'double minNumSpikes{sweptVarDims}[numWatchedAPCounts]')
                lines.append(indent3 + f'double maxNumSpikes{sweptVarDims}[numWatchedAPCounts]')
                lines.append(indent3 + f'double sumNumSpikes{sweptVarDims}[numWatchedAPCounts]')
                
        if isAnySweptVars or isRepeatForStats:
            lines.append(indent + '} else {')   # Extending "if (simIdx == 1) {"
            if isExportAltRunControl:
                lines.append(indent2 + 'altRunControlWidget.dismissHandler()')
                
        if isExportAltRunControl:
            if isAnySweptVars and isRepeatForStats:
                lines.append(indent3)
            if isAnySweptVars:
                if isRepeatForStats:
                    lines.append(indent3 + 'if (repIdx == 1) {')
                    indent4 = indent3 + stdIndent
                else:
                    lines.append(indent2)
                    indent4 = indent2
                lines.append(indent4 + 'execute("rngUtils.resetAllSeeds()")')
                if isRepeatForStats:
                    lines.append(indent3 + '} else {')
                    lines.append(indent4 + 'execute("rngUtils.setAllSeeds(uniqueSeedForHoc, uniqueSeedForMod)")')
                    lines.append(indent3 + '}')
                    
        if isAnySweptVars or isRepeatForStats:
            if isExportAltRunControl:
                lines.append(indent2)
            lines.append(indent2 + 'load_file(1, tempHocFilePathName)')
            lines.append(indent + '}')  # Closing "if (simIdx == 1) {"
            
        lines.append(indent)
        
        if isAnyWatchedVars:
            lines.append(indent + 'setUpVarVecsForRecording()')
            
        if isAnyWatchedAPCounts:
            lines.append(indent + 'setUpVecsForRecordingFromAPCounts()')
            
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append(indent)
            
        if not isExportAltRunControl:
            lines.append(indent + 'run()')
        else:
            lines.append(indent + 'alt_run()')
            
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append(indent)
            lines.append(indent + 'timestamp = pyObj.ev(getTimestampPyCommand)')
            
        if isAnySweptVars or isRepeatForStats:
            lines.append(indent)
            lines.append(indent + 'if (stoprun) {')
            lines.append(indent2 + 'stop')
            lines.append(indent + '}')
            
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append(indent)
            self._consumeWatchedData(lines, indent)
            
        if isAnySweptVars or isRepeatForStats:
            lines.append(indent)
            lines.append(indent + 'simIdx += 1')
            
        if isAnySweptVars:
            self._closeSweptVarCycles(lines, numSweptVars, indent)
            
        if isRepeatForStats:
            lines.append('}')   # Closing "for repIdx = 1, numRepeatsForStats {"
            
        if (isAnySweptVars or isRepeatForStats) and (isAnyWatchedVars or isAnyWatchedAPCounts):
            lines.append('')
            lines.append('if (stoprun) {')
            lines.append(stdIndent + '// Consuming the watched data one last time even though it\'s incomplete this time because user clicked "Stop"')
            self._consumeWatchedData(lines, stdIndent)
            lines.append('}')
            
        if isRepeatForStats and isAnyWatchedAPCounts:
            lines.append('')
            lines.append('saveAPCountsRepSummaryFile()')
            
        if isAnySweptVars or isRepeatForStats:
            lines.append('')
            lines.append('deleteTempFolder()')
            
        lines.append('')
        line = 'strdef word'
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            line += ', getAbsPathPyCommand, outBaseFolderAbsPath'
        lines.append(line)
        lines.append('if (stoprun) {')
        lines.append('    word = "Stopped"')
        lines.append('} else {')
        lines.append('    word = "Complete"')
        lines.append('}')
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append('{ sprint(getAbsPathPyCommand, "(exec(\'import os\'), os.path.abspath(\'%s\'))[1]", outBaseFolder) }')
            lines.append('outBaseFolderAbsPath = pyObj.ev(getAbsPathPyCommand)')
            lines.append(r'{ printf("\n%s!\nThe results were saved to \"%s\"\n\n", word, outBaseFolderAbsPath) }')
        else:
            lines.append(r'{ printf("\n%s!\n\n", word) }')
            
        return lines
        
        
    def _insertAllLinesFromRunnerHocUtilsFile(self, fileName):
        basePath = '_Code\\Export\\OutHocFileStructures\\RunnerHocUtils\\'
        return getAllLinesFromFile(basePath + fileName)
        
    def _openSweptVarCycles(self, lines, sweptVarsList, indent):
        
        numSweptVars = len(sweptVarsList)
        
        for sweptVarIdx in range(numSweptVars):
            lines.append(indent + f'for sweptVar{sweptVarIdx + 1}Idx = 0, sweptVar{sweptVarIdx + 1}GridSize - 1 {{')
            indent += stdIndent
            
            sweptVar = sweptVarsList[sweptVarIdx]
            lines.append(indent + '// ' + sweptVar.s)
            
            lines.append(indent + f'{getSweptVarName(sweptVarIdx)} = sweptVar{sweptVarIdx + 1}Grid[sweptVar{sweptVarIdx + 1}Idx]')
            
            lines.append(indent)
            
        return indent
        
    def _closeSweptVarCycles(self, lines, numSweptVars, indent):
        for sweptVarIdx in range(numSweptVars - 1, -1, -1):
            indent = indent[: -indentSize]
            lines.append(indent + '}')  # Closing "for sweptVar*Idx = 0, sweptVar*GridSize - 1 {"
            
    def _consumeWatchedData(self, lines, indent):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if isAnyWatchedVars:
            lines.append(indent + 'saveRecordedVarVecs()')
        if isAnyWatchedAPCounts:
            lines.append(indent + 'saveRecordedVecsFromAPCounts()')
            if isAnySweptVars:
                lines.append(indent + 'appendOneDataRowToAPCountsSweepSummaryFile()')
            if isRepeatForStats:
                lines.append(indent + 'updateDataForAPCountsRepSummaryFile()   // This uses sweptVar*Idx')
                