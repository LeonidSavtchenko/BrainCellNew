
import json
from neuron import h
from BiophysJsonExportCore import BiophysJsonExportCore
from BiophysJsonImportCore import BiophysJsonImportCore
from OtherInterModularUtils import *


class BiophysJsonFileHelper:
    
    _biophysJsonExportCore = BiophysJsonExportCore()
    _biophysJsonImportCore = BiophysJsonImportCore()
    
    _jsonDictForImportStage3 = None
    
    
    def exportStage2(self, outJsonFilePathName, options):
        
        jsonDict = self._biophysJsonExportCore.exportCore(options)
        
        with open(outJsonFilePathName, 'w') as jsonFile:
            json.dump(jsonDict, jsonFile, indent=4)
            
        return 0
        
    def importStage1(self, inJsonFilePathName):
        
        with open(inJsonFilePathName) as jsonFile:
            jsonDict = json.load(jsonFile)
            
        mechNames = set()
        
        compNames = h.List()
        numInhomVars = 0
        numStochVars = 0
        for (compName, mechNameToInfoDict) in jsonDict.items():
            compNames.append(h.String(compName))
            mechNames.update(mechNameToInfoDict.keys())
            for varTypeToInfoDict in mechNameToInfoDict.values():
                for varNameToInfoDict in varTypeToInfoDict.values():
                    for varValueOrInfoDict in varNameToInfoDict.values():
                        if type(varValueOrInfoDict) is not dict:
                            continue
                        for varInfoKey in varValueOrInfoDict.keys():
                            if varInfoKey == 'inhom_model':
                                numInhomVars += 1
                            elif varInfoKey == 'stoch_model':
                                numStochVars += 1
                                
        missingMechNames = h.List()
        for mechName in mechNames:
            if self._isMechMissing(mechName):
                missingMechNames.append(h.String(mechName))
                
        if missingMechNames:
            hocObj.mwh.showWarningBox(
                "Cannot import this biophys file because it uses some mechs missing in the local library \"nrnmech.dll\":", \
                missingMechNames)
            return 1
            
        self._jsonDictForImportStage3 = jsonDict
        
        hocObj.beih.importStage2(compNames, numInhomVars, numStochVars)     # --> importStage3
        
        return 0
        
    def importStage3(self, options):
        return self._biophysJsonImportCore.importCore(self._jsonDictForImportStage3, options)
        
        
    def _isMechMissing(self, mechName):
        # !!!!!!! very risky: the name can be declared as an arbitrary var rather than a mech
        #         re-implement this in a more robust way
        # !!! try to check type() in Python or object_id in HOC
        return not h.name_declared(mechName)    # !!! try to use it with 2nd arg; the docs say it returns the type code
        