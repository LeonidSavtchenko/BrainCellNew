
from neuron import h
from Utils.OtherUtils import *


class GensForInhomAndStochModels:
    
    # Data members that will be added in the ctor (they all depend on hoc:ExportOptions, so we defer the construction):
    #   _exportOptions
    
    def __init__(self):
        self._exportOptions = hocObj.exportOptions
        
    def createInhomBiophysModels(self):
        if not self._exportOptions.isExportAnyInhomBiophysModels():
            return emptyParagraphHint()
            
        selector = lambda actSpecVar : self._exportOptions.isExportedInhomBiophysVar(actSpecVar)
        lines = self._createAllInhomModels(selector)
        
        lines.append('{ inhomAndStochLibrary.applyAllBiophysInhomModels() }')
        
        return lines
        
    def createStochBiophysModels(self):
        if not self._exportOptions.isExportAnyStochBiophysModels():
            return emptyParagraphHint()
            
        selector = lambda actSpecVar : self._exportOptions.isExportedStochBiophysVar(actSpecVar)
        lines = self._createAllStochModels(selector)
        
        return lines
        
    def createInhomSynModels(self):
        if not self._exportOptions.isExportAnyInhomSynModels():
            return emptyParagraphHint()
            
        lines = []
        
        selector = lambda actSpecVar : self._exportOptions.isExportedInhomSynVar(actSpecVar)
        newLines = self._createAllInhomModels(selector)
        lines.extend(newLines)
        
        return lines
        
    def createStochSynModels(self):
        if not self._exportOptions.isExportAnyStochSynModels():
            return emptyParagraphHint()
            
        lines = []
        
        selector = lambda actSpecVar : self._exportOptions.isExportedStochSynVar(actSpecVar)
        newLines = self._createAllStochModels(selector)
        lines.extend(newLines)
        
        return lines
        
        
    def _createAllInhomModels(self, selector):
        lines = []
        
        for actSpecVar in h.inhomAndStochLibrary.activeSpecVars:
            if not selector(actSpecVar):
                continue
                
            distFuncHelper = actSpecVar.distFuncHelper
            segmentationHelper = actSpecVar.segmentationHelper
            
            if segmentationHelper is not None:
                lines.append('segmentationHelper = new ReducedSegmentationHelper()')
                lines.append('segmentationHelper.segmentationMode = {}'.format(int(segmentationHelper.segmentationMode)))
                lines.append('segmentationHelper.total_nseg = {}'.format(int(segmentationHelper.total_nseg)))
                lines.append('segmentationHelper.min_nseg = {}'.format(int(segmentationHelper.min_nseg)))
            else:
                lines.append('segmentationHelper = nil')
                
            newLines = self._createAndInitOneDistOrStochFuncHelper(distFuncHelper, 'distFuncHelper')
            lines.extend(newLines)
            
            lines.append('{{ inhomAndStochLibrary.onInhomCreate({}, {}, {}, {}, {}, {}, segmentationHelper, distFuncHelper, {}, {}) }}'.format(int(actSpecVar.enumDmPpNc), int(actSpecVar.compIdx), int(actSpecVar.mechIdx), int(actSpecVar.varType), int(actSpecVar.varIdx), int(actSpecVar.arrayIndex), int(actSpecVar.distFuncCatIdx), int(actSpecVar.distFuncIdx)))
            lines.append('')
            
        return lines
        
    def _createAllStochModels(self, selector):
        lines = []
        
        for actSpecVar in h.inhomAndStochLibrary.activeSpecVars:
            if not selector(actSpecVar):
                continue
                
            boundingHelper = actSpecVar.boundingHelper
            colourizationHelper = boundingHelper.colourizationHelper
            stochFuncHelper = actSpecVar.stochFuncHelper
            
            lines.append('colourizationHelper = new ColourizationHelper()')
            lines.append('colourizationHelper.chromaticity = {}'.format(int(colourizationHelper.chromaticity)))
            lines.append('colourizationHelper.colour = {}'.format(int(colourizationHelper.colour)))
            lines.append('colourizationHelper.alpha = {}'.format(colourizationHelper.alpha))
            lines.append('{ colourizationHelper.consumeSettings() }')
            
            lines.append('boundingHelper = new BoundingHelper(colourizationHelper)')
            lines.append('boundingHelper.where = {}'.format(int(boundingHelper.where)))
            lines.append('boundingHelper.mode = {}'.format(int(boundingHelper.mode)))
            lines.append('boundingHelper.min = {}'.format(boundingHelper.min))
            lines.append('boundingHelper.max = {}'.format(boundingHelper.max))
            
            newLines = self._createAndInitOneDistOrStochFuncHelper(stochFuncHelper, 'stochFuncHelper')
            lines.extend(newLines)
            
            lines.append('{{ inhomAndStochLibrary.onStochApply({}, {}, {}, {}, {}, {}, boundingHelper, stochFuncHelper, {}, {}) }}'.format(int(actSpecVar.enumDmPpNc), int(actSpecVar.compIdx), int(actSpecVar.mechIdx), int(actSpecVar.varType), int(actSpecVar.varIdx), int(actSpecVar.arrayIndex), int(actSpecVar.stochFuncCatIdx), int(actSpecVar.stochFuncIdx)))
            lines.append('')
            
        return lines
        
    def _createAndInitOneDistOrStochFuncHelper(self, distOrStochFuncHelper, varName):
        lines = []
        
        templName = getTemplateName(distOrStochFuncHelper)
        lines.append('{} = new {}()'.format(varName, templName))
        lines.append('vecOfVals = new Vector()')
        vecOfVals = h.Vector()
        listOfStrs = h.List()
        distOrStochFuncHelper.exportParams(vecOfVals, listOfStrs)
        for value in vecOfVals:
            lines.append('{{ vecOfVals.append({}) }}'.format(value))    # Max. precision is applied here automatically
        lines.append('listOfStrs = new List()')
        for thisStr in listOfStrs:
            thisStr = thisStr.s.replace('\n', '\\n')    # Needed for TablePlusLinInterp*FuncHelper 
            lines.append('{{ listOfStrs.append(new String("{}")) }}'.format(thisStr))
        lines.append('{{ {}.importParams(vecOfVals, listOfStrs) }}'.format(varName))
        
        return lines
        