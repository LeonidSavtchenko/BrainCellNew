
import os
import json
from neuron import hoc

# !!!! encapsulate all the code here into a class


_settingsDirPath = os.getcwd() + '\\..\\..\\Mechanisms\\Settings\\'


def _ms_loadJsonFileAndDeleteHintKey(fileName, keyToDel):
    with open(_settingsDirPath + fileName) as jsonFile:
        jsonDict = json.load(jsonFile)
        try:
            del jsonDict[keyToDel]
        except KeyError:
            pass
    return jsonDict
    
_ms_jsonDict1 = _ms_loadJsonFileAndDeleteHintKey('hide_stoch_btn_for.json', 'JustExampleOfMechName')
_ms_jsonDict2 = _ms_loadJsonFileAndDeleteHintKey('diffusible_species.json', 'Legend')


def ms_isHideStochButton(mechName, varNameWithIndex):
    return mechName in _ms_jsonDict1 and varNameWithIndex in _ms_jsonDict1[mechName]
    
    
def ms_setIonGlobalVars():
    hocObj = hoc.HocObject()    # !!! move it to the enclosing class level or better unify with the one created in Export module
    for subDict in _ms_jsonDict2.values():
        for value in subDict.values():
            ionMechName = value['ionMechName']
            suffix = ms_ionMechNameToSuffix(ionMechName)
            baseInnerConc = value['baseInnerConc (mM)']
            baseOuterConc = value["baseOuterConc (mM)"]
            try:
                setattr(hocObj, f'{suffix}i0_{suffix}_ion', baseInnerConc)
                setattr(hocObj, f'{suffix}o0_{suffix}_ion', baseOuterConc)
            except LookupError:
                # The ion is present in JSON file, but missing in MOD files
                # !!! it would be better to skip the assignment attempt rather than suppress the error
                #     (can user have such vars in HOC without having the ion?)
                pass
                
def ms_getAllSpcCatNames():
    return list(_ms_jsonDict2.keys())
    
def ms_getTotalNumExpIons():
    numIons = 0
    for subDict in _ms_jsonDict2.values():
        numIons += len(subDict)
    return numIons
    
def ms_getAllExpIonNames():
    lst = []
    for spcCatName in _ms_jsonDict2:
        lst.extend(ms_getAllExpIonNamesInThisCat(spcCatName))
    return lst
    
def ms_getAllExpIonNamesInThisCat(spcCatName):
    lst = []
    for value in _ms_jsonDict2[spcCatName].values():
        lst.append(value['ionMechName'])
    return lst
    
def ms_getUserFriendlyIonNameOrEmpty(actIonName):
    for subDict in _ms_jsonDict2.values():
        for key, value in subDict.items():
            if value['ionMechName'] == actIonName:
                return key
    return ''
    
def ms_isActIonInThisCat(actIonName, spcCatName):
    return any(value['ionMechName'] == actIonName for value in _ms_jsonDict2[spcCatName].values())
    
def ms_getDiff(spcCatName, actIonName):
    for value in _ms_jsonDict2[spcCatName].values():
        if value['ionMechName'] == actIonName:
            return value['Diff (um2/ms)']
    raise Error     # !!! replace with either codeContractViolation or an error saying that the JSON file is malformed
    
    
# !!! maybe move to some intermodular utils
def ms_getPyListItem(pyList, hocIdx):
    return pyList[int(hocIdx)]
    
# !!! maybe move to some intermodular utils
def ms_ionMechNameToSuffix(ionMechName):
    ionSuffix = '_ion'          # !!! already defined in HOC
    if not ionMechName.endswith(ionSuffix):
        raise Error     # !!! replace with either codeContractViolation or an error saying that the JSON file is malformed
    return ionMechName[: -len(ionSuffix)]
    