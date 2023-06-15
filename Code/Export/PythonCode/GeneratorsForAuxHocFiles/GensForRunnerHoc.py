
from Utils.UnitsUtils import UnitsUtils
from Utils.OtherUtils import *


class GensForRunnerHoc:
    
    # Data members that will be added in the ctor:
    #   _exportOptions
    #   _outMainHocFileName
    
    def __init__(self, outMainHocFileName):
        self._exportOptions = hocObj.exportOptions
        self._outMainHocFileName = outMainHocFileName
        
    def getPrologue(self):
        lines = []
        lines.append('strdef runnedHocFileName, outFolderName')
        lines.append('runnedHocFileName = "{}"'.format(self._outMainHocFileName))
        lines.append('outFolderName = "results"')
        return lines
        
    def getSweptVars(self):
        if not self._exportOptions.isAnySweptVars():
            return emptyParagraphHint()
            
        lines = []
        
        sweptVarsList = self._exportOptions.sweptVarsList
        numSweptVars = len(sweptVarsList)
        
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
        if not self._exportOptions.isAnyWatchedVars():
            return emptyParagraphHint()
            
        lines = []
        
        watchedVarsList = self._exportOptions.watchedVarsList
        
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
        lines.append('numItersPerOneRecord = {}'.format(int(self._exportOptions.numItersPerOneRecord)))
        lines.append('')
        
        lines.append('// Hint: use "%g" for compact format and "%.15e" for max precision')
        lines.append('strdef oneValueFormat')
        lines.append('oneValueFormat = "%-8.4g"')
        
        return lines
        
    def getUtils(self):
        if not (self._exportOptions.isAnySweptVars() or self._exportOptions.isAnyWatchedVars()):
            # !!!! maybe it doesn't make sense to create "runner.hoc" in this case
            return emptyParagraphHint()
            
        # !!!! we need to filter these utils and export only the required ones depending on self._exportOptions
        relFilePathName = 'Code\\Export\\OutHocFileStructures\\RunnerHocUtils.hoc'
        return getAllLinesFromFile(relFilePathName)
        
    def getPrerequisites(self):
        if not (self._exportOptions.isAnySweptVars() or self._exportOptions.isAnyWatchedVars()):
            # !!!! maybe it doesn't make sense to create "runner.hoc" in this case
            return emptyParagraphHint()
            
        return getAllLinesFromFile('Code\\Export\\OutHocFileStructures\\PythonCheck.hoc')
        
    def getMainPart(self):
        lines = []
        
        isAnySweptVars = self._exportOptions.isAnySweptVars()
        isAnyWatchedVars = self._exportOptions.isAnyWatchedVars()
        
        numSweptVars = len(self._exportOptions.sweptVarsList)
        
        if isAnySweptVars or isAnyWatchedVars:
            lines.append('createTempHocFileWithoutTemplatesAndOutputFolder()')
            lines.append('')
            
        indent = ''
        
        if isAnySweptVars:
            lines.append(r'print "\nTo stop the entire process, click \"Tools -> RunControl -> Stop\" or uncheck \"Tools -> RunButton -> Init & Run\".\n"')
            lines.append('')
            
        if isAnySweptVars or isAnyWatchedVars:
            # !!!! if isAnyWatchedVars, we need this to name the file (a temp solution)
            lines.append('simIdx = 1')
            lines.append('')
            
        if isAnySweptVars:
            for sweptVarIdx in range(numSweptVars):
                lines.append(indent + f'for sweptVar{sweptVarIdx + 1}Idx = 0, sweptVar{sweptVarIdx + 1}GridSize - 1 {{')
                indent += stdIndent
                lines.append(indent + f'{getSweptVarName(sweptVarIdx)} = sweptVar{sweptVarIdx + 1}Grid[sweptVar{sweptVarIdx + 1}Idx]')
                lines.append(indent)
            lines.append(indent + r'printf("Running simulation %d of %d ...\n", simIdx, totalNumSims)')
        else:
            lines.append(indent + r'{ printf("\nRunning simulation ...\n") }')
        lines.append(indent)
        
        extraIndent = indent + stdIndent
        
        if not isAnySweptVars:
            lines.append(indent + '{ load_file(runnedHocFileName) }')
        else:
            lines.append(indent + 'if (simIdx == 1) {')
            lines.append(extraIndent + 'load_file(runnedHocFileName)')
            lines.append(indent + '} else {')
            lines.append(extraIndent + 'load_file(1, tempHocFilePathName)')
            lines.append(indent + '}')
        lines.append(indent)
        
        if isAnyWatchedVars:
            lines.append(indent + '// Both "dt" and "tstop" can be swept')
            lines.append(indent + 'Dt = numItersPerOneRecord * dt')
            lines.append(indent + 'numRecs = tstop / Dt + 1')       # !!!! test it when tstop / Dt is not integer
            lines.append(indent)
            lines.append(indent + 'setUpVecsForRecording()')
            lines.append(indent)
            
        lines.append(indent + 'run()')
        
        if isAnySweptVars:
            lines.append(indent)
            lines.append(indent + 'if (stoprun) {')
            lines.append(extraIndent + 'stop')
            lines.append(indent + '}')
        
        if isAnyWatchedVars:
            lines.append(indent)
            lines.append(indent + 'saveRecordedVecs()')
            
        if isAnySweptVars:
            lines.append(indent)
            lines.append(indent + 'simIdx += 1')
            
            for sweptVarIdx in range(numSweptVars - 1, -1, -1):
                indent = indent[: -indentSize]
                lines.append(indent + '}')
                
        if isAnySweptVars or isAnyWatchedVars:
            lines.append('')
            lines.append('deleteTempFolder()')
            
        # !!!! these messages must be different if user stopped the cycle
        lines.append('')
        if isAnyWatchedVars:
            lines.append(r'{ printf("\nComplete!\nThe results were saved to \"%s%s\"\n\n", getcwd(), outFolderName) }')
        else:
            lines.append(r'{ printf("\nComplete!\n\n") }')
            
        return lines
        