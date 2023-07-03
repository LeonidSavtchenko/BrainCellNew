
from Utils.UnitsUtils import UnitsUtils
from Utils.OtherUtils import *


class GensForRunnerHoc:
    
    # Data member that will be added in the ctor:
    #   _outMainHocFileName
    
    def __init__(self, outMainHocFileName):
        self._outMainHocFileName = outMainHocFileName
        
    def getPrologue(self):
        lines = []
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        varNames = []
        varNames.append('runnedHocFileName')
        if isAnySweptVars or isRepeatForStats or isAnyWatchedVars or isAnyWatchedAPCounts:
            varNames.append('outFolderName')    # Used by createTempHocFileWithoutTemplatesAndOutputFolder
        if (isAnyWatchedVars or isAnyWatchedAPCounts) and isRepeatForStats:
            varNames.append('outFolderNameFormat')
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            varNames.append('outFileNameTimestampFormat')
        lines.append('strdef ' + ', '.join(varNames))
        
        lines.append('runnedHocFileName = "{}"'.format(self._outMainHocFileName))
        
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            if not isRepeatForStats:
                lines.append('outFolderName = "results"')
            else:
                lines.append('outFolderNameFormat = "results %d"')
            lines.append('outFileNameTimestampFormat = "%Y-%m-%d %H.%M.%S"')
            
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
                    userReadableName = sweptVar.s.replace('\\', '\\\\') + UnitsUtils.getUnitsCommentOrEmptyForExposedOrSweptVar1(sweptVar)
                    lines.append(f'{{ sweptVarUserReadableNames.append(new String("{userReadableName}")) }}')
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
            totalNumSimsExpr = ' * '.join([f'sweptVar{sweptVarIdx + 1}GridSize' for sweptVarIdx in range(numSweptVars)])
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
            
        lines.append('// Format hints:')
        lines.append('//  "%g"     - mid precision, jagged columns (compact format)')
        lines.append('//  "%.15e"  - max precision, fixed column width (with exponent)')
        lines.append('//  "%-8.4g" - low precision, fixed column width (left alignment)')
        lines.append('//  "%8.4g"  - low precision, fixed column width (right alignment)')
        lines.append('//  "%.15g"  - max precision, jagged columns (compact format, without ".0")')
        lines.append('//  "@py"    - max precision, jagged columns (compact format, with ".0")')
        lines.append('strdef oneValueFormat')
        lines.append('oneValueFormat = "%-8.4g"')
        
        return lines
        
    def getUtils(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isAnySweptVars or isRepeatForStats or isAnyWatchedVars or isAnyWatchedAPCounts):
            # !! maybe it doesn't make sense to create "runner.hoc" in this case
            return emptyParagraphHint()
            
        lines = []
        
        basePath = 'Code\\Export\\OutHocFileStructures\\RunnerHocUtils\\'
        
        if isAnySweptVars or isRepeatForStats or isAnyWatchedVars or isAnyWatchedAPCounts:
            newLines = getAllLinesFromFile('Code\\InterModular\\Exported\\InterModularErrWarnUtilsPart1_Exported.hoc')
            lines.extend(newLines)
            lines.append('')
            
            newLines = getAllLinesFromFile(basePath + 'RunnerHocCreateUtils.hoc')
            lines.extend(newLines)
            
        if isAnySweptVars or isRepeatForStats:
            lines.append('')
            newLines = getAllLinesFromFile(basePath + 'RunnerHocDeleteUtils.hoc')
            lines.extend(newLines)
            
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            if len(lines) != 0:
                lines.append('')
            newLines = getAllLinesFromFile(basePath + 'RunnerHocWatchedUtils.hoc')
            lines.extend(newLines)
            lines.append('')
            if isAnySweptVars:
                lines.append('numSweptVars = sweptVarUserReadableNames.count()')
            else:
                lines.append('numSweptVars = 0')
                
        if isAnyWatchedVars:
            lines.append('')
            newLines = getAllLinesFromFile(basePath + 'RunnerHocWatchedVarsUtils.hoc')
            lines.extend(newLines)
            
        if isAnyWatchedAPCounts:
            lines.append('')
            newLines = getAllLinesFromFile(basePath + 'RunnerHocWatchedAPCountsUtils.hoc')
            lines.extend(newLines)
            
        if (isAnyWatchedVars or isAnyWatchedAPCounts) and isAnySweptVars:
            lines.append('')
            newLines = getAllLinesFromFile(basePath + 'RunnerHocSweptVarsUtils.hoc')
            lines.extend(newLines)
            
        return lines
        
    def getPrerequisites(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isAnySweptVars or isRepeatForStats or isAnyWatchedVars or isAnyWatchedAPCounts):
            # !! maybe it doesn't make sense to create "runner.hoc" in this case
            return emptyParagraphHint()
            
        lines = getAllLinesFromFile('Code\\Export\\OutHocFileStructures\\PythonCheck.hoc')
        
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append('')
            newLines = getAllLinesFromFile('Code\\Export\\OutHocFileStructures\\RunnerHocUtils\\RunnerHocWatchedVarsPrereqs.hoc')
            lines.extend(newLines)
            
        return lines
        
    def getMainPart(self):
        lines = []
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isRepeatForStats = hocObj.exportOptions.isRepeatForStats
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        isExportAltRunControl = hocObj.exportOptions.isExportAltRunControl()
        
        sweptVarsList = hocObj.exportOptions.sweptVarsList
        numSweptVars = len(sweptVarsList)
        
        if isAnySweptVars or isRepeatForStats or isAnyWatchedVars or isAnyWatchedAPCounts:
            isCreateTempHocFileWithoutTemplates = isAnySweptVars or isRepeatForStats
            isCreateOrCleanUpOutFolder = (isAnyWatchedVars or isAnyWatchedAPCounts) and not isRepeatForStats
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
        else:
            lines.append('nrncontrolmenu()')
            lines.append('')
            
        if isRepeatForStats and isExportAltRunControl:
            lines.append('uniqueSeedForHoc = -1')
            lines.append('uniqueSeedForMod = -1')
            lines.append('')
            
        if isAnySweptVars or isRepeatForStats:
            lines.append('simIdx = 1')
            lines.append('')
            
        if isRepeatForStats:
            lines.append('for repIdx = 1, numRepeatsForStats {')
            indent = stdIndent
            if isAnyWatchedVars or isAnyWatchedAPCounts:
                lines.append(indent + 'sprint(outFolderName, outFolderNameFormat, repIdx)')
                lines.append(indent + 'createTempHocFileWithoutTemplatesAndOutputFolder("False", "True")')
            lines.append(indent)
            if isExportAltRunControl:
                lines.append(indent + 'if (repIdx != 1) {')
                extraIndent = indent + stdIndent
                # Avoiding "object prefix is NULL", we use "execute" here instead of "objref rngUtils" upstream
                # because we'll call makeSureDeclared("rngUtils") downstream and need to have the object NOT declared
                lines.append(extraIndent + 'execute("rngUtils.getAllSeeds(&uniqueSeedForHoc, &uniqueSeedForMod)")')
                lines.append(extraIndent + 'uniqueSeedForHoc += 1')
                lines.append(extraIndent + 'uniqueSeedForMod += 1')
                lines.append(indent + '}')
                lines.append(indent)
        else:
            indent = ''
            
        if isAnySweptVars:
            for sweptVarIdx in range(numSweptVars):
                lines.append(indent + f'for sweptVar{sweptVarIdx + 1}Idx = 0, sweptVar{sweptVarIdx + 1}GridSize - 1 {{')
                indent += stdIndent
                
                sweptVar = sweptVarsList[sweptVarIdx]
                lines.append(indent + '// ' + sweptVar.s)
                
                lines.append(indent + f'{getSweptVarName(sweptVarIdx)} = sweptVar{sweptVarIdx + 1}Grid[sweptVar{sweptVarIdx + 1}Idx]')
                
                lines.append(indent)
                
        if isAnySweptVars or isRepeatForStats:
            lines.append(indent + r'printf("Running simulation %d of %d ...\n", simIdx, totalNumSims)')
        else:
            lines.append(indent + r'{ printf("\nRunning simulation ...\n") }')
        lines.append(indent)
        
        extraIndent = indent + stdIndent
        
        if not (isAnySweptVars or isRepeatForStats):
            lines.append(indent + '{ load_file(runnedHocFileName) }')
            indent_ = indent
        else:
            lines.append(indent + 'if (simIdx == 1) {')
            lines.append(extraIndent + 'load_file(runnedHocFileName)')
            indent_ = extraIndent
            
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append(indent_)
            lines.append(indent_ + 'checkCVodePrerequisites()')
            
        if isAnyWatchedAPCounts:
            lines.append(indent_)
            lines.append(indent_ + 'apcList = new List("APCount")')
            lines.append(indent_ + 'numWatchedAPCounts = apcList.count()')
            lines.append(indent_ + 'objref recordedVecsFromAPCounts[numWatchedAPCounts]')
            
        if isAnySweptVars or isRepeatForStats:
            lines.append(indent + '} else {')
            if isExportAltRunControl:
                lines.append(extraIndent + 'altRunControlWidget.dismissHandler()')
                lines.append(extraIndent)
            lines.append(extraIndent + 'load_file(1, tempHocFilePathName)')
            
        if isRepeatForStats and isExportAltRunControl:
            lines.append(indent_)
            lines.append(indent_ + 'if (repIdx != 1) {')
            lines.append(indent_ + stdIndent + 'execute("rngUtils.setAllSeeds(uniqueSeedForHoc, uniqueSeedForMod)")')
            lines.append(indent_ + '}')
            
        if isAnySweptVars or isRepeatForStats:
            lines.append(indent + '}')
            
        lines.append(indent)
        
        if isAnyWatchedVars:
            lines.append(indent + 'setUpVarVecsForRecording()')
            lines.append(indent)
            
        if isAnyWatchedAPCounts:
            lines.append(indent + 'setUpVecsForRecordingFromAPCounts()')
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
            lines.append(extraIndent + 'stop')
            lines.append(indent + '}')
            
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append(indent)
            if isAnySweptVars or isRepeatForStats:
                lines.append(indent + 'if (simIdx != totalNumSims) {')
                indent_ = extraIndent
            else:
                indent_ = indent
                
            if isAnyWatchedVars:
                lines.append(indent_ + 'saveRecordedVarVecs()')
            if isAnyWatchedAPCounts:
                lines.append(indent_ + 'saveRecordedVecsFromAPCounts()')
                
            if isAnySweptVars or isRepeatForStats:
                lines.append(indent + '}')
                
        if isAnySweptVars or isRepeatForStats:
            lines.append(indent)
            lines.append(indent + 'simIdx += 1')
            
            for sweptVarIdx in range(numSweptVars - 1, -1, -1):
                indent = indent[: -indentSize]
                lines.append(indent + '}')
                
        if isRepeatForStats:
            lines.append('}')
            
        if (isAnySweptVars or isRepeatForStats) and (isAnyWatchedVars or isAnyWatchedAPCounts):
            lines.append('')
            lines.append('// Saving the vecs on the last iteration AND in case when user breaks the cycle by simulations')
            if isAnyWatchedVars:
                lines.append('saveRecordedVarVecs()')
            if isAnyWatchedAPCounts:
                lines.append('saveRecordedVecsFromAPCounts()')
                
        if isAnySweptVars or isRepeatForStats:
            lines.append('')
            lines.append('deleteTempFolder()')
            
        lines.append('')
        lines.append('strdef word')
        lines.append('if (stoprun) {')
        lines.append('    word = "Stopped"')
        lines.append('} else {')
        lines.append('    word = "Complete"')
        lines.append('}')
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            if not isRepeatForStats:
                varName = 'outFolderName'
            else:
                varName = 'outFolderNameFormat'
            lines.append(r'{ printf("\n%s!\nThe results were saved to \"%s%s\"\n\n", word, getcwd(), ' + varName + ') }')
        else:
            lines.append(r'{ printf("\n%s!\n\n", word) }')
            
        return lines
        