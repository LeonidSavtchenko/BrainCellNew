
from neuron import h, hoc
from OtherUtils import *


class GeneratorsForAuxHocFiles:
    
    _hocObj = hoc.HocObject()
    
    # Other data members that will be added in the ctor:
    #   _exportOptions
    
    def __init__(self):
        self._exportOptions = self._hocObj.exportOptions
        
    def getParamsCode(self):
        lines = []
        
        isAnyExposedVars = self._exportOptions.isAnyExposedVars()
        
        if isAnyExposedVars:
            exposedVarsList = self._exportOptions.exposedVarsList
            for exposedVarIdx in range(len(exposedVarsList)):
                lines.append('')
                exposedVar = exposedVarsList[exposedVarIdx]
                lines.append(f'// {exposedVar.s}{self._getUnitsComment(exposedVar)}')
                lines.append(f'{getExposedVarName(exposedVarIdx)} = {exposedVar.getValue()}')
                
        return lines
        
    def getRunnerCode(self, outMainHocFileName):
        lines = []
        
        indentSize = 4
        
        sweptVarsList = self._exportOptions.sweptVarsList
        watchedVarsList = self._exportOptions.watchedVarsList
        
        numSweptVars = len(sweptVarsList)
        numWatchedVars = len(watchedVarsList)
        
        isAnySweptVars = self._exportOptions.isAnySweptVars()
        isAnyWatchedVars = self._exportOptions.isAnyWatchedVars()
        
        lines.append('')
        
        if isAnySweptVars:
            for sweptVarIdx in range(numSweptVars):
                sweptVar = sweptVarsList[sweptVarIdx]
                lines.append(f'// {sweptVar.s}{self._getUnitsComment(sweptVar)}')
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
                
        if isAnyWatchedVars:
            lines.append('objref ' + ', '.join([f'watchedVarIdx{watchedVarIdx + 1}Vec' for watchedVarIdx in range(numWatchedVars)]))
            for watchedVarIdx in range(numWatchedVars):
                lines.append(f'watchedVarIdx{watchedVarIdx + 1}Vec = new Vector()    // {watchedVarsList[watchedVarIdx].s}')
            lines.append('')
            
        if isAnySweptVars:
            lines.append('simIdx = 1')
            lines.append('totalNumSims = ' + ' * '.join([f'sweptVar{sweptVarIdx + 1}GridSize' for sweptVarIdx in range(numSweptVars)]))
            lines.append('')
            lines.append(r'print "\nTo stop the entire process, click \"Tools -> RunControl -> Stop\" or uncheck \"Tools -> RunButton -> Init & Run\".\n"')
            lines.append('')
            
        indent = ''
        if isAnySweptVars:
            for sweptVarIdx in range(numSweptVars):
                lines.append(indent + f'for sweptVar{sweptVarIdx + 1}Idx = 0, sweptVar{sweptVarIdx + 1}GridSize - 1 {{')
                indent += ' ' * indentSize
                lines.append(indent + f'{getSweptVarName(sweptVarIdx)} = sweptVar{sweptVarIdx + 1}Grid[sweptVar{sweptVarIdx + 1}Idx]')
                lines.append(indent)
                
            lines.append(indent + 'printf("Running simulation %d of %d ...\\n", simIdx, totalNumSims)')
            lines.append(indent)
            
        lines.append(indent + f'load_file(1, "{outMainHocFileName}")')
        lines.append(indent)
        
        if isAnyWatchedVars:
            if isAnySweptVars:
                lines.append(indent + 'if (simIdx == 1) {')
                indent_ = indent + ' ' * indentSize
                self._addVectorRecordCommands(indent_, numWatchedVars, watchedVarsList, lines)
                lines.append(indent + '}')
            else:
                self._addVectorRecordCommands(indent, numWatchedVars, watchedVarsList, lines)
            lines.append(indent)
            
        lines.append(indent + 'run()')
        lines.append(indent)
        
        if isAnySweptVars:
            lines.append(indent + 'if (stoprun) {')
            lines.append(indent + '    stop')
            lines.append(indent + '}')
            lines.append(indent)
            
        lines.append(indent + '// !! save all recorded Vector-s')
        
        if isAnyWatchedVars:
            lines.append(indent)
            for watchedVarIdx in range(numWatchedVars):
                lines.append(indent + f'watchedVarIdx{watchedVarIdx + 1}Vec.resize(0)')
                
        if isAnySweptVars:
            lines.append(indent)
            lines.append(indent + 'simIdx += 1')
            
            for sweptVarIdx in range(numSweptVars - 1, -1, -1):
                indent = indent[: -indentSize]
                lines.append(indent + '}')
                
        return lines
        
        
    def _getUnitsComment(self, var):
        if var.enumSpDmCe != 2:
            isDmOrSynPart = var.enumSpDmCe
            enumDmPpNc = self._hocObj.compUtils.getComp(isDmOrSynPart, var.compIdx).enumDmPpNc
            units = h.ref('')
            self._hocObj.mth.getVarUnits(enumDmPpNc, var.mechIdx, var.varName, var.varNameWithIndex, units)
            units = units[0]
        else:
            units = h.units(var.customExpr)
            
        if units:
            return f' ({units})'
        else:
            return ''
            
    def _addVectorRecordCommands(self, indent, numWatchedVars, watchedVarsList, lines):
        for watchedVarIdx in range(numWatchedVars):
            lines.append(indent + f'execute("watchedVarIdx{watchedVarIdx + 1}Vec.record(&{watchedVarsList[watchedVarIdx].s})")')
            