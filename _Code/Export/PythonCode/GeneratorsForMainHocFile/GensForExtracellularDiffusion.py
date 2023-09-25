
from Utils.UnitsUtils import UnitsUtils
from Utils.OtherUtils import *


class GensForExtracellularDiffusion:

    def createSpeciesLibrary(self):
        if not hocObj.exportOptions.isExportExtracellularLibrary():
            return emptyParagraphHint()
            
        lines = []
        
        speciesLibrary = hocObj.speciesLibrary
        
        lines.append('// GLOBAL-s')
        
        hocCommand1Templ = '{} = {}    // ({})'
        
        # !!!! just a temp solution: these GLOBAL-s will be exported as a part of biophysics once we implement it
        # !!!! but even before this, maybe move this initialization of GLOBAL-s to a separate paragraph for carity
        
        # !!! make sure py:ms_setIonGlobalVars or legacy code don't rewrite them just after import in "start with nano" mode
        #     UPD: py:ms_setIonGlobalVars is called before the exported HOC file starts assigning the new values
        for (globalVarName, _) in self._eachSpcInfoInLibExceptUnrecCat():
            value = getattr(hocObj, globalVarName)
            
            # !!! maybe use some other util or at least rename this one
            units = UnitsUtils.getUnitsForWatchedVar(globalVarName)
            
            lines.append(hocCommand1Templ.format(globalVarName, value, units))
            
        lines.append('')
        lines.append('begintemplate ReducedSpeciesLibrary')
        lines.append('')
        lines.append('    public copyGlobalVarsToModParams, packToVec, getSpeciesFlatIdxForModInterface')
        lines.append('    ')
        lines.append('    external stringsEqual, codeContractViolation')
        lines.append('    ')
        lines.append('    ')
        lines.append('    proc copyGlobalVarsToModParams() {')
        
        hocCommand2Templ = 'execute("{}oinit_ECDCalcAndConsHelper = {}")'
        
        for (globalVarName, suffix) in self._eachSpcInfoInLibExceptUnrecCat():
            lines.append('        ' + hocCommand2Templ.format(suffix, globalVarName))
            
        lines.append('    }')
        lines.append('    ')
        
        lines.append('    obfunc packToVec() { localobj vec')
        spcLibPackedToVec = speciesLibrary.packToVec()
        n = len(spcLibPackedToVec)
        lines.append(f'        vec = new Vector({n})')
        for idx in range(n):
            # !!! think about creating a common util for exporting vectors (use it here, for spineNeckDiamCache and maybe for DistFunc-s and StochFunc-s)
            lines.append(f'        vec.x[{idx}] = {spcLibPackedToVec[idx]}')    # !!! maybe use int(*) for the first value
        lines.append('        return vec')
        lines.append('    }')
        lines.append('    ')
        
        lines.append('    func getSpeciesFlatIdxForModInterface() { local spcCatIdx')
        lines.append('        strdef species')
        lines.append('        ')
        lines.append('        spcCatIdx = $1')
        lines.append('        species = $s2')
        lines.append('        ')
        spcCatsList = speciesLibrary.spcCatsList
        isFirstIter1 = True
        for spcCatIdx in range(len(spcCatsList)):
            op = self._getIfOrElseIfOperator(isFirstIter1)
            lines.append(f'        {op} (spcCatIdx == {spcCatIdx}) {{')
            isFirstIter2 = True
            for spcName in spcCatsList[spcCatIdx].spcNamesList:
                op = self._getIfOrElseIfOperator(isFirstIter2)
                species = spcName.s
                lines.append(f'            {op} (stringsEqual(species, "{species}")) {{')
                lines.append(f'                return {int(speciesLibrary.getSpeciesFlatIdxForModInterface(spcCatIdx, species))}')
                isFirstIter2 = False
            lines.append('            }')
            isFirstIter1 = False
        lines.append('        }')
        lines.append('        codeContractViolation()')
        lines.append('    }')
        lines.append('    ')
        lines.append('endtemplate ReducedSpeciesLibrary')
        lines.append('')
        lines.append('objref speciesLibrary')
        lines.append('speciesLibrary = new ReducedSpeciesLibrary()')
        
        return lines
        
    def createSourcesLibrary(self):
        if not hocObj.exportOptions.isExportExtracellularLibrary():
            return emptyParagraphHint()
            
        lines = []
        
        lines.append('objref ecsLibrary')
        lines.append('')
        
        relDirPath = '_Code\\Extracellular\\ExtracellularSourcesLibrary\\Exported'
        ecslTemplNames = [
            'ECLDeploymentCache',
            'ECSSpatialInfo',
            'ECSTemporalInfo',
            'ECSCapacityInfo',
            'ECSSeriesInfo',        # !!! maybe don't export if no series
            'ExtracellularSource',
            'ExtracellularSourcesLibrary']
        exportTheseTemplatesFromThisDir(lines, relDirPath, ecslTemplNames)
        
        # !!! the order of export is not the same as in "ExtracellularManagerLoads.hoc" -- need to test
        lines.append('')
        newLines = getAllLinesFromFile('_Code\\Extracellular\\Utils\\ExtracellularApplicatorUtils_Exported.hoc')
        lines.extend(newLines)
        
        return lines
        
    def createExtraDiffFinale(self):
        if not hocObj.exportOptions.isExportExtracellularLibrary():
            return emptyParagraphHint()
            
        lines = []
        
        lines.append('objref spatialInfo, temporalInfo, capacityInfo, seriesInfo')
        lines.append('')
        ecsList = hocObj.ecsLibrary.ecsList
        
        for ecs in ecsList:
            lines.append('// ' + ecs.s)
            lines.append(f'spatialInfo = new ECSSpatialInfo({self._getSpatialInfoCtorArgs(ecs.spatialInfo)})')
            lines.append(f'temporalInfo = new ECSTemporalInfo({self._getTemporalInfoCtorArgs(ecs.temporalInfo)})')
            lines.append(f'capacityInfo = new ECSCapacityInfo({self._getCapacityInfoCtorArgs(ecs.spatialInfo.enumPointSphere, ecs.temporalInfo.enumStaticSwitchSpike, ecs.capacityInfo)})')
            isSeries = (ecs.temporalInfo.isSeriesOrMinus1 == 1)
            if isSeries:
                lines.append(f'seriesInfo = new ECSSeriesInfo({self._getSeriesInfoCtorArgs(ecs.seriesInfoOrNil)})')
            lines.append(f'{{ ecsLibrary.addNewSource({self._getExtracellularSourceCtorArgs(ecs, isSeries)}) }}')
            lines.append('')
            
        lines.append('applyExtracellularSources()')
        
        return lines
        
        
    # !!!! make them @classmethod ?
    
    def _eachSpcInfoInLibExceptUnrecCat(self):
        globalVarNameTempl = '{}o0_{}_ion'  # !!! do I need to export "io" vars as well?
        # !!! it looks like we cannot use HOC iterators from Python, but need to double check
        #       for spcInfo? in hocObj.speciesLibrary.eachSpcInfoInLibExceptUnrecCat(spcInfo?):
        # !!! Keep in sync with hoc:SpeciesLibrary.eachSpcInfoInLibExceptUnrecCat
        for spcCat in hocObj.speciesLibrary.spcCatsList:
            if spcCat.isUnrecSpcCat:
                continue
            for spcInfo in spcCat.spcInfoList:
                suffix = spcInfo.suffix
                globalVarName = globalVarNameTempl.format(suffix, suffix)
                yield (globalVarName, suffix)
                
    def _getIfOrElseIfOperator(self, isFirstIter):
        if isFirstIter:
            return 'if'
        else:
            return '} else if'
            
    def _getSpatialInfoCtorArgs(self, spatialInfo):
        enumPointSphere = int(spatialInfo.enumPointSphere)
        x = spatialInfo.x
        y = spatialInfo.y
        z = spatialInfo.z
        radiusOrMinus1 = spatialInfo.radiusOrMinus1
        
        args = [enumPointSphere, x, y, z]
        
        if enumPointSphere == 0:
            # Empty by design
            pass
        elif enumPointSphere == 1:
            self._makeSureNotMinus1ThenAppend(args, radiusOrMinus1)
        else:
            codeContractViolation()
            
        return self._toCSV(args)
        
    def _getTemporalInfoCtorArgs(self, temporalInfo):
        enumStaticSwitchSpike = int(temporalInfo.enumStaticSwitchSpike)
        offsetTimeOrMinus1 = temporalInfo.offsetTimeOrMinus1
        durationOrMinus1 = temporalInfo.durationOrMinus1
        isSeriesOrMinus1 = int(temporalInfo.isSeriesOrMinus1)
        
        args = [enumStaticSwitchSpike]
        
        if enumStaticSwitchSpike == 0:
            # Empty by design
            pass
        elif enumStaticSwitchSpike == 1:
            self._makeSureNotMinus1ThenAppend(args, offsetTimeOrMinus1, durationOrMinus1, isSeriesOrMinus1)
        elif enumStaticSwitchSpike == 2:
            self._makeSureNotMinus1ThenAppend(args, offsetTimeOrMinus1, isSeriesOrMinus1)
        else:
            codeContractViolation()
            
        return self._toCSV(args)
        
    def _getCapacityInfoCtorArgs(self, enumPointSphere, enumStaticSwitchSpike, capacityInfo):
        enumPointSphere = int(enumPointSphere)
        enumStaticSwitchSpike = int(enumStaticSwitchSpike)
        
        ssOrMinus1 = capacityInfo.ssOrMinus1
        pointCapacityRadiusOrMinus1 = capacityInfo.pointCapacityRadiusOrMinus1
        numMoleculesOrMinus1 = capacityInfo.numMoleculesOrMinus1    # !!! int(*) ?
        delta_oOrMinus1 = capacityInfo.delta_oOrMinus1
        
        args = [enumPointSphere]
        
        if enumPointSphere == 0:
            args.append(enumStaticSwitchSpike)
            if enumStaticSwitchSpike < 2:
                self._makeSureNotMinus1ThenAppend(args, ssOrMinus1, pointCapacityRadiusOrMinus1)
            elif enumStaticSwitchSpike == 2:
                self._makeSureNotMinus1ThenAppend(args, numMoleculesOrMinus1)
            else:
                codeContractViolation()
        elif enumPointSphere == 1:
            if enumStaticSwitchSpike > 2:
                codeContractViolation()
            self._makeSureNotMinus1ThenAppend(args, delta_oOrMinus1)
        else:
            codeContractViolation()
            
        return self._toCSV(args)
        
    def _getSeriesInfoCtorArgs(self, seriesInfo):
        mechStd = seriesInfo.mechStd
        
        interval = mechStd.get('interval')
        number = mechStd.get('number')  # !!! maybe need to use int(*) here, but NEURON is OK with a fractional value
        start = mechStd.get('start')
        noise = mechStd.get('noise')    # Don't add int(*) here
        
        args = [interval, number, start, noise]
        
        return self._toCSV(args)
        
    def _getExtracellularSourceCtorArgs(self, ecs, isSeries):
        spcCatIdx = int(ecs.spcCatIdx)
        species = '"' + ecs.species + '"'
        
        args = [spcCatIdx, species, 'spatialInfo', 'temporalInfo', 'capacityInfo']
        if isSeries:
            args.append('seriesInfo')
            
        return self._toCSV(args)
        
    def _makeSureNotMinus1ThenAppend(self, args, *newArgs):
        for newArg in newArgs:
            if newArg == -1:
                codeContractViolation()
            args.append(newArg)
            
    def _toCSV(self, args):
        return ', '.join(str(arg) for arg in args)
        