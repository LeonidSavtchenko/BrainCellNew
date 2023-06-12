
import os, shutil
from neuron import h, hoc, nrn
from GeneratorsForMainHocFile.GeneratorsForMainHocFile import *
from GeneratorsForAuxHocFiles.GeneratorsForAuxHocFiles import *
from Utils.OtherUtils import *


_genStartMarker = 'py:'
_genEndMarker = ')'
_parStartMarker = '//////////////////// Start of '
_parEndMarker = '//////////////////// End of '
_emptyParMarker = emptyParagraphHint()


class _GenInfo:
    
    def __init__(self, startIdx, endIdx, pyCall):
        self.startIdx = startIdx
        self.endIdx = endIdx
        self.pyCall = pyCall
        
        
def exportCore(outMainHocFilePathName):
    
    hocObj = hoc.HocObject()
    _exportMainHocFile(outMainHocFilePathName, hocObj)
    
    outDirPath = os.path.dirname(outMainHocFilePathName)
    outMainHocFileName = os.path.basename(outMainHocFilePathName)
    exportOptions = hocObj.exportOptions
    
    if exportOptions.isCreateParamsHoc or exportOptions.isCreateRunnerHoc:
        _exportAuxHocFiles(outDirPath, outMainHocFileName, exportOptions)
        
    if exportOptions.isCopyDll:
        _copyMechsDllFile(outDirPath, hocObj.mechsDllUtils.loadedDllDirPath)
        
        
def _exportMainHocFile(outMainHocFilePathName, hocObj):
    
    isAstrocyteOrNeuron = hocObj.isAstrocyteOrNeuron
    
    if isAstrocyteOrNeuron:
        inSkeletonFileName = 'OutHocFileSkeletonForAstrocyte.txt'
    else:
        inSkeletonFileName = 'OutHocFileSkeletonForNeuron.txt'
    inSkeletonFileRelPathName = 'Code\\Export\\OutHocFileStructures\\Skeletons\\' + inSkeletonFileName
    
    with open(inSkeletonFileRelPathName, 'r') as inFile:
        lines = inFile.readlines()      # Preserving all newline characters here
        
    lineIdxToGenInfoDict = _findAllGenerators(lines)
    
    gens = GeneratorsForMainHocFile()
    
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
            codeContractViolation()
            
    _removeEmptyParagraphs(lines)
    
    _prependTableOfContents(lines)
    
    with open(outMainHocFilePathName, 'w') as outFile:
        outFile.writelines(lines)
        
def _exportAuxHocFiles(outDirPath, outMainHocFileName, exportOptions):
    
    gens = GeneratorsForAuxHocFiles()
    
    if exportOptions.isCreateParamsHoc:
        lines = gens.getParamsCode()
        _saveAuxHocFile(lines, outDirPath, 'params.hoc')
        
    if exportOptions.isCreateRunnerHoc:
        lines = gens.getRunnerCode(outMainHocFileName)
        _saveAuxHocFile(lines, outDirPath, 'runner.hoc')
        
def _saveAuxHocFile(lines, outDirPath, outFileName):
    lines = _addNewLineChars(lines)
    filePathName = outDirPath + '\\' + outFileName
    with open(filePathName, 'w') as outFile:
        outFile.writelines(lines)
        
def _copyMechsDllFile(outDirPath, loadedDllDirPath):
    
    dllFileName = 'nrnmech.dll'
    
    srcDllFilePath = loadedDllDirPath + '\\' + dllFileName
    dstDllFilePath = outDirPath + '/' + dllFileName     # Will be printed in case of shutil.PermissionError
    
    try:
        shutil.copyfile(srcDllFilePath, dstDllFilePath)
    except shutil.SameFileError:
        # Maybe user loaded a nano HOC file exported earlier and now just exports it again
        pass
    
def _findAllGenerators(lines):
    lineIdxToGenInfoDict = {}
    for lineIdx in range(len(lines)):
        line = lines[lineIdx]
        startIdx = line.find(_genStartMarker)
        if startIdx == -1:
            continue
        pyCallIdx = startIdx + len(_genStartMarker)
        endIdx = line.find(_genEndMarker, pyCallIdx)
        if endIdx == -1:
            codeContractViolation()
        endIdx += 1
        testIdx = line.find(_genStartMarker, endIdx)
        if testIdx != -1:
            # More than 1 generator in the same line: Not implemented
            codeContractViolation()
        lineIdxToGenInfoDict[lineIdx] = _GenInfo(startIdx, endIdx, line[pyCallIdx : endIdx])
    return lineIdxToGenInfoDict
    
def _removeEmptyParagraphs(lines):
    lineIdx = len(lines) - 1
    while lineIdx > 0:
        line = lines[lineIdx]
        if line.startswith(_emptyParMarker):
            if lines[lineIdx - 3] != '\n' or not lines[lineIdx - 2].startswith(_parStartMarker) or not lines[lineIdx + 2].startswith(_parEndMarker):
                codeContractViolation()
            lines[lineIdx - 3 : lineIdx + 3] = []
            lineIdx -= 4
        else:
            lineIdx -= 1
            
def _prependTableOfContents(lines):
    hdrStartIdx = len(_parStartMarker)
    lineIdxToHeaderDict = {}
    for lineIdx in range(len(lines)):
        line = lines[lineIdx]
        if not line.startswith(_parStartMarker):
            continue
        hdrEndIdx = line.find(' /', hdrStartIdx)
        if hdrEndIdx == -1:
            codeContractViolation()
        header = line[hdrStartIdx : hdrEndIdx]
        header = header[0].upper() + header[1 :]
        lineIdxToHeaderDict[lineIdx] = header
    if len(lineIdxToHeaderDict) == 0:
        codeContractViolation()
    numToCLines = len(lineIdxToHeaderDict) + 5
    genLines = []
    genLines.append('//////////////////// Table of contents ///////////////////////////////////')
    genLines.append('/*')
    for lineIdx, header in lineIdxToHeaderDict.items():
        linePtr = '    Line {}: '.format(lineIdx + numToCLines)
        spacer = ' ' * (24 - len(linePtr))
        genLines.append('{}{}{}'.format(linePtr, spacer, header))
    genLines.append('*/')
    genLines.append('//////////////////////////////////////////////////////////////////////////')
    lines[: 0] = _addNewLineChars(genLines)
    
def _insertSubstring(lines, lineIdx, startIdx, endIdx, genSubstring):
    line = lines[lineIdx]
    line = line[: startIdx] + genSubstring + line[endIdx :]
    lines[lineIdx] = line
    
def _insertLines(lines, lineIdx, genLines):
    lines[lineIdx : lineIdx + 1] = _addNewLineChars(genLines)
    
def _addNewLineChars(genLines):
    return [genLine + '\n' for genLine in genLines]
    