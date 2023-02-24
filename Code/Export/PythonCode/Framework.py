
from neuron import hoc, nrn
from Generators import *


# !! maybe create a class and encapsulate it inside
genStartMarker = 'py:'
genEndMarker = ')'

class _GenInfo:
    """!!"""
    
    def __init__(self, startIdx, endIdx, pyCall):
        """!!"""
        self.startIdx = startIdx
        self.endIdx = endIdx
        self.pyCall = pyCall
        
def exportCore(outHocFilePathName):
    """!!
    Other input: isAstrocyteOrNeuron (taken from the top level)"""
    
    hocObj = hoc.HocObject()
    isAstrocyteOrNeuron = hocObj.isAstrocyteOrNeuron
    
    if isAstrocyteOrNeuron:
        inSkeletonFileName = 'OutHocFileSkeletonForAstrocyte.txt'
    else:
        inSkeletonFileName = 'OutHocFileSkeletonForNeuron.txt'
    inSkeletonFileRelPathName = 'Code\\Export\\OutHocFileSkeletons\\' + inSkeletonFileName
    
    with open(inSkeletonFileRelPathName, 'r') as inFile:
        lines = inFile.readlines()      # Preserving all newline characters here
    
    lineIdxToGenInfoDict = _findAllGenerators(lines)
    
    gens = Generators()
    
    # Iterating in reverse order to keep the line indexes intact
    lineIdxs = list(lineIdxToGenInfoDict.keys())
    for lineIdx in reversed(lineIdxs):
        genInfo = lineIdxToGenInfoDict[lineIdx]
        genRes = eval('gens.' + genInfo.pyCall)
        tp = type(genRes)
        if tp == str:
            _insertSubstring(lines, lineIdx, genInfo.startIdx, genInfo.endIdx, genRes)
        elif tp == list:
            _insertLines(lines, lineIdx, genRes)
        else:
            _codeContractViolation()
    
    with open(outHocFilePathName, 'w') as outFile:
        outFile.writelines(lines)

def _findAllGenerators(lines):
    """!!"""
    lineIdxToGenInfoDict = {}
    for lineIdx in range(len(lines)):
        line = lines[lineIdx]
        startIdx = line.find(genStartMarker)
        if startIdx == -1:
            continue
        pyCallIdx = startIdx + len(genStartMarker)
        endIdx = line.find(genEndMarker, pyCallIdx)
        if endIdx == -1:
            _codeContractViolation()
        endIdx += 1
        testIdx = line.find(genStartMarker, endIdx)
        if testIdx != -1:
            # More than 1 generator in the same line: Not implemented
            _codeContractViolation()
        lineIdxToGenInfoDict[lineIdx] = _GenInfo(startIdx, endIdx, line[pyCallIdx : endIdx])
    return lineIdxToGenInfoDict

def _insertSubstring(lines, lineIdx, startIdx, endIdx, genSubstring):
    """!!"""
    line = lines[lineIdx]
    line = line[: startIdx] + genSubstring + line[endIdx :]
    lines[lineIdx] = line

def _insertLines(lines, lineIdx, genLines):
    """!!"""
    lines[lineIdx : lineIdx + 1] = [genLine + '\n' for genLine in genLines]
    
    
def _codeContractViolation():
    raise Exception('Bug in Exporter: Code contract violation')
