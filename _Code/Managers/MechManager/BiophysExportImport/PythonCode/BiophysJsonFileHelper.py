
import json
from neuron import h, hoc


hocObj = hoc.HocObject()


class BiophysJsonFileHelper:

    def exportStage2(self, outJsonFilePathName, options):
        # !!!
        print('!!! exportStage2')
        
        # !!!
        self._printOptions(options)
        
        return 0    # !!!
        
    def importStage1(self, inJsonFilePathName):
        # !!!
        print('!!! importStage1')
        
        with open(inJsonFilePathName) as jsonFile:
            jsonDict = json.load(jsonFile)
            
        compNames = h.List()
        numInhomVars = 0
        numStochVars = 0
        for (compName, mechNameToInfoDict) in jsonDict.items():
            compNames.append(h.String(compName))
            for varTypeToInfoDict in mechNameToInfoDict.values():
                if type(varTypeToInfoDict) == str:                      # !!!!!!!! just a temp shortcut (encountered a comment in the test JSON)
                    continue
                for varRecordToInfoDict in varTypeToInfoDict.values():
                    if type(varRecordToInfoDict) == str:                # !!!!!!!! just a temp shortcut (encountered "..." in the test JSON)
                        continue
                    for varRecordKey in varRecordToInfoDict.keys():
                        if 'inhom' in varRecordKey:         # !!! a bit risky approach because the marker can appear in the units
                            numInhomVars += 1
                        if 'stoch' in varRecordKey:         # !!! the same comment
                            numStochVars += 1
                            
        """ !!!
        compNames.append(h.String('Soma'))
        compNames.append(h.String('Dendrites'))
        compNames.append(h.String('Axon'))
        compNames.append(h.String('Spine Neck'))
        compNames.append(h.String('Spine Head'))
        compNames.append(h.String('Comp Test 1'))
        compNames.append(h.String('Comp Test 2'))
        compNames.append(h.String('Comp Test 3'))
        compNames.append(h.String('Comp Test 4'))
        compNames.append(h.String('Comp Test 5'))
        compNames.append(h.String('Comp Test 6'))
        compNames.append(h.String('Comp Test 7'))
        compNames.append(h.String('Comp Test 8'))
        compNames.append(h.String('Comp Test 9'))
        compNames.append(h.String('Comp Test 10'))
        numInhomVars = 222
        numStochVars = 333
        """
        
        hocObj.beih.importStage2(compNames, numInhomVars, numStochVars)
        
        return 0    # !!!
        
    def importStage3(self, options):
        # !!!
        print('!!! importStage3')
        
        # !!!
        self._printOptions(options)
        
        return 0    # !!!
        
        
    # !!!
    def _printOptions(self, options):
        print('-----')
        print('options.isUseThisCompNameVec.size(): ', options.isUseThisCompNameVec.size())
        print('options.isUseThisCompNameVec.sum(): ', options.isUseThisCompNameVec.sum())
        print('options.isGlobals: ', options.isGlobals)
        print('options.isAssignedAndState: ', options.isAssignedAndState)
        print('options.isInhoms: ', options.isInhoms)
        print('options.isStochs: ', options.isStochs)
        