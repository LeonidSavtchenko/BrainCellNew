
from Utils.UnitsUtils import UnitsUtils
from Utils.OtherUtils import *


class GensForRunnerHoc:
    
    # Data member that will be added in the ctor:
    #   _outMainHocFileName
    
    def __init__(self, outMainHocFileName):
        self._outMainHocFileName = outMainHocFileName
        
    def getPrologue(self):
        lines = []
        
        line2 = 'runnedHocFileName = "{}"'.format(self._outMainHocFileName)
        
        if hocObj.exportOptions.isAnySweptVars() or hocObj.exportOptions.isAnyWatchedVars() or hocObj.exportOptions.isAnyWatchedAPCounts():
            # !!!! if not (hocObj.exportOptions.isAnyWatchedVars() or hocObj.exportOptions.isAnyWatchedAPCounts()),
            #      then there is no need to define "outFolderName" and "outFileNameTimestampFormat",
            #      but currently "outFolderName" accessed from hoc:createTempHocFileWithoutTemplatesAndOutputFolder, and skipping it here would lead to an error
            lines.append('strdef runnedHocFileName, outFolderName, outFileNameTimestampFormat')
            lines.append(line2)
            lines.append('outFolderName = "results"')
            lines.append('outFileNameTimestampFormat = "%Y-%m-%d %H.%M.%S"')
        else:
            lines.append('strdef runnedHocFileName')
            lines.append(line2)
            
        return lines
        
    def getSweptVars(self):
        if not hocObj.exportOptions.isAnySweptVars():
            return emptyParagraphHint()
            
        lines = []
        
        sweptVarsList = hocObj.exportOptions.sweptVarsList
        numSweptVars = len(sweptVarsList)
        
        if hocObj.exportOptions.isAnyWatchedVars():
            lines.append('objref sweptVarUserReadableNames')
            lines.append('sweptVarUserReadableNames = new List()')
            for sweptVar in sweptVarsList:
                userReadableName = sweptVar.s.replace('\\', '\\\\') + UnitsUtils.getUnitsCommentForExposedOrSweptVar(sweptVar)
                lines.append(f'{{ sweptVarUserReadableNames.append(new String("{userReadableName}")) }}')
            lines.append('')
            
        for sweptVarIdx in range(numSweptVars):
            sweptVar = sweptVarsList[sweptVarIdx]
            lines.append(f'// {sweptVar.s}{UnitsUtils.getUnitsCommentForExposedOrSweptVar(sweptVar)}')
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
            
        lines.append('totalNumSims = ' + ' * '.join([f'sweptVar{sweptVarIdx + 1}GridSize' for sweptVarIdx in range(numSweptVars)]))
        
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
            
            lines.append('// We\'ll record the values only once per "numItersPerOneRecord" iterations (it must be a positive integer)')
            lines.append('numItersPerOneRecord = {}'.format(int(hocObj.exportOptions.numItersPerOneRecord)))
            lines.append('')
            
        lines.append('// Hint: use "%g" for compact format and "%.15e" for max precision')
        lines.append('strdef oneValueFormat')
        lines.append('oneValueFormat = "%-8.4g"')
        
        return lines
        
    def getUtils(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isAnySweptVars or isAnyWatchedVars or isAnyWatchedAPCounts):
            # !!!! maybe it doesn't make sense to create "runner.hoc" in this case
            return emptyParagraphHint()
            
        lines = []
        
        basePath = 'Code\\Export\\OutHocFileStructures\\RunnerHocUtils\\'
        
        if isAnySweptVars or isAnyWatchedVars:
            newLines = getAllLinesFromFile('Code\\InterModular\\Exported\\InterModularErrWarnUtilsPart1_Exported.hoc')
            lines.extend(newLines)
            lines.append('')
            
            newLines = getAllLinesFromFile(basePath + 'RunnerHocBasicUtils.hoc')
            lines.extend(newLines)
            
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            if len(lines) != 0:
                lines.append('')
            if isAnySweptVars:
                lines.append('numSweptVars = sweptVarUserReadableNames.count()')
            else:
                lines.append('numSweptVars = 0')
                
        if isAnyWatchedVars:
            lines.append('')
            newLines = getAllLinesFromFile(basePath + 'RunnerHocWatchedVarsUtils.hoc')
            lines.extend(newLines)
            
            if isAnySweptVars:
                lines.append('')
                newLines = getAllLinesFromFile(basePath + 'RunnerHocSweptVarsUtils.hoc')
                lines.extend(newLines)
                
        if isAnyWatchedAPCounts:
            lines.append('')
            newLines = getAllLinesFromFile(basePath + 'RunnerHocWatchedAPCountsUtils.hoc')
            lines.extend(newLines)
            
        return lines
        
    def getPrerequisites(self):
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        if not (isAnySweptVars or isAnyWatchedVars or isAnyWatchedAPCounts):
            # !!!! maybe it doesn't make sense to create "runner.hoc" in this case
            return emptyParagraphHint()
            
        lines = getAllLinesFromFile('Code\\Export\\OutHocFileStructures\\PythonCheck.hoc')
        
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append('')
            lines.append('pyObj = new PythonObject()')
            lines.append('{ nrnpython("ev = lambda arg : eval(arg)") }')
            
        return lines
        
    def getMainPart(self):
        lines = []
        
        isAnySweptVars = hocObj.exportOptions.isAnySweptVars()
        isAnyWatchedVars = hocObj.exportOptions.isAnyWatchedVars()
        isAnyWatchedAPCounts = hocObj.exportOptions.isAnyWatchedAPCounts()
        
        sweptVarsList = hocObj.exportOptions.sweptVarsList
        numSweptVars = len(sweptVarsList)
        
        if isAnySweptVars or isAnyWatchedVars:
            lines.append('createTempHocFileWithoutTemplatesAndOutputFolder()')
            lines.append('')
            
        indent = ''
        
        if isAnySweptVars:
            lines.append(r'print "\nIf you need to break the cycle by simulations, just Stop the current simulation.\n"')
            lines.append('')
            
        if not hocObj.exportOptions.isExportReducedRNGUtils():
            lines.append('nrncontrolmenu()')
            lines.append('')
            
        if isAnySweptVars:
            lines.append('simIdx = 1')
            lines.append('')
            
        if isAnySweptVars:
            for sweptVarIdx in range(numSweptVars):
                lines.append(indent + f'for sweptVar{sweptVarIdx + 1}Idx = 0, sweptVar{sweptVarIdx + 1}GridSize - 1 {{')
                indent += stdIndent
                
                sweptVar = sweptVarsList[sweptVarIdx]
                lines.append(indent + '// ' + sweptVar.s)
                
                lines.append(indent + f'{getSweptVarName(sweptVarIdx)} = sweptVar{sweptVarIdx + 1}Grid[sweptVar{sweptVarIdx + 1}Idx]')
                
                lines.append(indent)
            lines.append(indent + r'printf("Running simulation %d of %d ...\n", simIdx, totalNumSims)')
        else:
            lines.append(indent + r'{ printf("\nRunning simulation ...\n") }')
        lines.append(indent)
        
        extraIndent = indent + stdIndent
        
        if not isAnySweptVars:
            lines.append(indent + '{ load_file(runnedHocFileName) }')
            if isAnyWatchedAPCounts:
                lines.append(indent)
                lines.append(indent + 'apcList = new List("APCount")')
                lines.append(indent + 'numWatchedAPCounts = apcList.count()')
                lines.append(indent + 'objref recordedVecsFromAPCounts[numWatchedAPCounts]')
        else:
            lines.append(indent + 'if (simIdx == 1) {')
            lines.append(extraIndent + 'load_file(runnedHocFileName)')
            if isAnyWatchedAPCounts:
                lines.append(extraIndent)
                lines.append(extraIndent + 'apcList = new List("APCount")')
                lines.append(extraIndent + 'numWatchedAPCounts = apcList.count()')
                lines.append(extraIndent + 'objref recordedVecsFromAPCounts[numWatchedAPCounts]')
            lines.append(indent + '} else {')
            lines.append(extraIndent + 'load_file(1, tempHocFilePathName)')
            lines.append(indent + '}')
        lines.append(indent)
        
        if isAnyWatchedVars:
            lines.append(indent + '// Letting NEURON change "dt" now rather than on start of the simulation,')
            lines.append(indent + '// so we can set up the recorders correctly')
            lines.append(indent + 'setdt()')
            lines.append(indent)
            lines.append(indent + '// Both "dt" and "tstop" can be swept')
            lines.append(indent + 'Dt = numItersPerOneRecord * dt')
            lines.append(indent + 'numRecs = tstop / Dt + 1')       # !!!! test it when tstop / Dt is not integer
            lines.append(indent)
            lines.append(indent + 'setUpVecsForRecording()')
            lines.append(indent)
            
        if isAnyWatchedAPCounts:
            lines.append(indent + 'setUpVecsForRecordingFromAPCounts()')
            lines.append(indent)
            
        if not hocObj.exportOptions.isExportReducedRNGUtils():
            lines.append(indent + 'run()')
        else:
            lines.append(indent + 'alt_run()')
            
        if isAnySweptVars:
            lines.append(indent)
            lines.append(indent + 'if (stoprun) {')
            lines.append(extraIndent + 'stop')
            lines.append(indent + '}')
            
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append(indent)
            if isAnySweptVars:
                lines.append(indent + 'if (simIdx != totalNumSims) {')
                indent_ = extraIndent
            else:
                indent_ = indent
                
            if isAnyWatchedVars:
                lines.append(indent_ + 'saveRecordedVecs()')
            if isAnyWatchedAPCounts:
                lines.append(indent_ + 'saveRecordedVecsFromAPCounts()')
                
            if isAnySweptVars:
                lines.append(indent + '}')
                
        if isAnySweptVars:
            lines.append(indent)
            lines.append(indent + 'simIdx += 1')
            
            for sweptVarIdx in range(numSweptVars - 1, -1, -1):
                indent = indent[: -indentSize]
                lines.append(indent + '}')
                
        if isAnySweptVars and (isAnyWatchedVars or isAnyWatchedAPCounts):
            lines.append('')
            lines.append('// This will save the vecs on the last iteration AND in case when user stops the cycle')
            if isAnyWatchedVars:
                lines.append('saveRecordedVecs()')
            if isAnyWatchedAPCounts:
                lines.append('saveRecordedVecsFromAPCounts()')
                
        if isAnySweptVars or isAnyWatchedVars:
            lines.append('')
            lines.append('deleteTempFolder()')
            
        # !!!! these messages must be different if user stopped the cycle
        lines.append('')
        if isAnyWatchedVars or isAnyWatchedAPCounts:
            lines.append(r'{ printf("\nComplete!\nThe results were saved to \"%s%s\"\n\n", getcwd(), outFolderName) }')
        else:
            lines.append(r'{ printf("\nComplete!\n\n") }')
            
        return lines
        