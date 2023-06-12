
from Utils.OtherUtils import *


class LoopUtils:
    
    # !! Currenly this method cannot produce the nested loops of depth 3 and higher.
    #    The depth 2 is sufficient to export astrocyte nanogeometry in the shortest way,
    #    but in general case it's not enough because the imported geometry file may store the sections
    #    in arbitrary n-dimentional structures
    def tryInsertLoopsToShorten(lines, useNestedLoops):
        lines, isShortened = LoopUtils._insertLoopsToShortenCore(lines, 'idx2', False)
        
        if isShortened and useNestedLoops:
            lines2 = LoopUtils._wrapInnerCycles(lines)
            lines2, isShortened = LoopUtils._insertLoopsToShortenCore(lines2, 'idx1', True)
            if isShortened:
                lines = LoopUtils._unwrapInnerCycles(lines2)
                
        return lines
        
    def _insertLoopsToShortenCore(lines, idxVarName, isSecondIteration):
    
        outLines = []
        
        isShortened = False
        
        isInsideBlock = False
        firstParsedIdx = -1
        prevParsedIdx = -1
        prevLine = ''
        prevParsedPattern = ''
        
        # !! it would be better to sort lines here because user could Merge/Split compartments and so shuffle the sections,
        #    but simple "sorted(lines)" won't work until we prepend each index with zeros so that all corresponding indices
        #    have the same length
        for line in lines:
            idx2 = LoopUtils._rfindExt(line, ']', isSecondIteration)
            if idx2 == -1:
                if isInsideBlock:
                    isShortened = LoopUtils._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName) or isShortened
                    isInsideBlock = False
                outLines.append(line)
                continue
            idx1 = LoopUtils._rfindExt(line, '[', isSecondIteration)
            if idx1 == -1:
                codeContractViolation()
            idx1 += 1
            thisParsedIdx = int(line[idx1 : idx2])
            thisParsedPattern = '{}{}{}'.format(line[: idx1], idxVarName, line[idx2 :])
            if not isInsideBlock:
                # Found a new block
                firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern = LoopUtils._startBlock(thisParsedIdx, line, thisParsedPattern)
                isInsideBlock = True
            else:
                if thisParsedPattern == prevParsedPattern and thisParsedIdx == prevParsedIdx + 1:
                    # Continue parsing this block
                    prevParsedIdx = thisParsedIdx
                else:
                    # The block is over
                    isShortened = LoopUtils._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName) or isShortened
                    firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern = LoopUtils._startBlock(thisParsedIdx, line, thisParsedPattern)
                    isInsideBlock = True
                    
        if isInsideBlock:
            isShortened = LoopUtils._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName) or isShortened
            
        return outLines, isShortened
        
    def _startBlock(thisParsedIdx, line, thisParsedPattern):
        return thisParsedIdx, thisParsedIdx, line, thisParsedPattern
        
    def _finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName):
        if prevParsedIdx != firstParsedIdx:
            outLines.append('    for {} = {}, {} {{'.format(idxVarName, firstParsedIdx, prevParsedIdx))
            outLines.append('    ' + prevParsedPattern)
            outLines.append('    }')
            return True
        else:
            outLines.append(prevLine)
            return False
            
    def _wrapInnerCycles(lines):
        outLines = []
        
        isInsideBlock = False
        linesBlock = []
        for line in lines:
            if ' for ' in line:
                isInsideBlock = True
                linesBlock.append(line)
            elif ' }' in line:
                linesBlock.append(line)
                outLines.append('\n'.join(linesBlock))
                isInsideBlock = False
                linesBlock = []
            elif isInsideBlock:
                linesBlock.append(line)
            else:
                outLines.append(line)
                
        if isInsideBlock:
            codeContractViolation()
            
        return outLines
        
    def _unwrapInnerCycles(lines):
        outLines = []
        for line in lines:
            if '\n' not in line:
                outLines.append(line)
                continue
            newLines = line.split('\n')
            firstLine = newLines[0]
            if firstLine.startswith('    for idx2 = '):
                indent = ''
            else:
                indent = '    '
            outLines.append(firstLine)
            newLines = [indent + newLine for newLine in newLines[1 :]]
            outLines.extend(newLines)
        return outLines
        
    def _rfindExt(line, marker, isSecondIteration):
        idx = line.rfind(marker)
        if idx == -1:
            return idx
        if isSecondIteration:
            idx = line.rfind(marker, 0, idx)
        return idx
        