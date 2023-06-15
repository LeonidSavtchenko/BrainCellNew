
from Utils.OtherUtils import *


class LoopUtils:
    
    # !! Currenly this method cannot produce the nested loops of depth 3 and higher.
    #    The depth 2 is sufficient to export astrocyte nanogeometry in the shortest way,
    #    but in general case it's not enough because the imported geometry file may store the sections
    #    in arbitrary n-dimentional structures
    def tryInsertLoopsToShorten(lines, useNestedLoops):
    
        if len(lines) == 0:
            return lines
            
        if useNestedLoops:
            idxVarName = 'idx2'
        else:
            idxVarName = 'idx'
        lines, isShortened, baseIndent = LoopUtils._insertLoopsToShortenCore(lines, idxVarName, False)
        
        if isShortened and useNestedLoops:
            lines2 = LoopUtils._wrapInnerCycles(lines, baseIndent)
            lines2, isShortened, _ = LoopUtils._insertLoopsToShortenCore(lines2, 'idx1', True)
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
        
        baseIndent = getIndent(lines[0])
        
        # !! it would be better to sort lines here because user could Merge/Split compartments and so shuffle the sections,
        #    but simple "sorted(lines)" won't work until we prepend each index with zeros so that all corresponding indices
        #    have the same length
        for line in lines:
            idx2 = LoopUtils._rfindExt(line, ']', isSecondIteration)
            if idx2 == -1:
                if isInsideBlock:
                    isShortened = LoopUtils._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName, baseIndent) or isShortened
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
                    isShortened = LoopUtils._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName, baseIndent) or isShortened
                    firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern = LoopUtils._startBlock(thisParsedIdx, line, thisParsedPattern)
                    isInsideBlock = True
                    
        if isInsideBlock:
            isShortened = LoopUtils._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName, baseIndent) or isShortened
            
        return outLines, isShortened, baseIndent
        
    def _startBlock(thisParsedIdx, line, thisParsedPattern):
        return thisParsedIdx, thisParsedIdx, line, thisParsedPattern
        
    def _finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName, baseIndent):
        if prevParsedIdx != firstParsedIdx:
            outLines.append(baseIndent + 'for {} = {}, {} {{'.format(idxVarName, firstParsedIdx, prevParsedIdx))
            
            newLines = prevParsedPattern.split('\n')
            newLines = [stdIndent + newLine for newLine in newLines]
            outLine = '\n'.join(newLines)
            outLines.append(outLine)
            
            outLines.append(baseIndent + '}')
            
            return True
        else:
            outLines.append(prevLine)
            return False
            
    def _wrapInnerCycles(lines, baseIndent):
        outLines = []
        
        isInsideBlock = False
        linesBlock = []
        for line in lines:
            if line.startswith(baseIndent + 'for '):
                isInsideBlock = True
                linesBlock.append(line)
            elif line.startswith(baseIndent + '}'):
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
            else:
                newLines = line.split('\n')
                outLines.extend(newLines)
        return outLines
        
    def _rfindExt(line, marker, isSecondIteration):
        idx = line.rfind(marker)
        if idx == -1:
            return idx
        if isSecondIteration:
            idx = line.rfind(marker, 0, idx)
        return idx
        