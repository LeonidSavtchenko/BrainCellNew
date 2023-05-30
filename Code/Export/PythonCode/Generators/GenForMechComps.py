
from neuron import hoc
from OtherUtils import *


class GenForMechComps:
    
    _hocObj = hoc.HocObject()
    
    # !! BUG: In rare cases, an error "procedure too big" may occur when user loads the exported file.
    #         This error takes place while sourcing one of obfunc-s named "getListOfSecRefsFor*Comp".
    #         The root cause is that the base geometry file imported earlier
    #         created so many sections on the top level, that we cannot create now in the scope of just one obfunc.
    #         To fix this error, we'll have to init all list_ref-s on the top level rather than in the obfunc-s.
    def createReducedMechComps(self):
    
        lines = []
        
        mmAllComps = self._hocObj.mmAllComps
        
        # Create number of obfunc-s to prepare "list_ref" for each comp
        obfuncNames = []
        for comp in mmAllComps:
            obfuncNameId = prepareUniqueNameId(comp.name)
            obfuncName = 'getListOfSecRefsFor{}Comp'.format(obfuncNameId)
            obfuncNames.append(obfuncName)
            lines.append('obfunc {}() {{ local idx1, idx2 localobj list_ref'.format(obfuncName))
            lines.append('    list_ref = new List()')
            newLines = []
            for sec_ref in comp.list_ref:
                newLines.append('    {} list_ref.append(new SectionRef())'.format(sec_ref.sec))
            newLines = self._insertLoopsToShorten(newLines)
            lines.extend(newLines)
            lines.append('    return list_ref')
            lines.append('}')
            lines.append('')
        
        lines.append('objref comp')
        lines.append('')
        lines.append('mmAllComps = new List()')
        lines.append('')
        
        for (comp, obfuncName) in zip(mmAllComps, obfuncNames):
            lines.append('comp = new ReducedMechComp("{}", {}())'.format(comp.name, obfuncName))
            lines.append('{ mmAllComps.append(comp) }')
            lines.append('')
            
        return lines
        
        
    # !! Currenly this method cannot produce the nested loops of depth 3 and higher.
    #    The depth 2 is sufficient to export astrocyte nanogeometry in the shortest way,
    #    but in general case it's not enough because the imported geometry file may store the sections
    #    in arbitrary n-dimentional structures
    def _insertLoopsToShorten(self, lines):
        lines, isShortened = self._insertLoopsToShortenCore(lines, 'idx2', False)
        
        if isShortened:
            lines2 = self._wrapInnerCycles(lines)
            lines2, isShortened = self._insertLoopsToShortenCore(lines2, 'idx1', True)
            if isShortened:
                lines = self._unwrapInnerCycles(lines2)
            
        return lines
        
    def _insertLoopsToShortenCore(self, lines, idxVarName, isSecondIteration):
    
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
            idx2 = self._rfindExt(line, ']', isSecondIteration)
            if idx2 == -1:
                if isInsideBlock:
                    isShortened = self._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName) or isShortened
                    isInsideBlock = False
                outLines.append(line)
                continue
            idx1 = self._rfindExt(line, '[', isSecondIteration)
            if idx1 == -1:
                codeContractViolation()
            idx1 += 1
            thisParsedIdx = int(line[idx1 : idx2])
            thisParsedPattern = '{}{}{}'.format(line[: idx1], idxVarName, line[idx2 :])
            if not isInsideBlock:
                # Found a new block
                firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern = self._startBlock(thisParsedIdx, line, thisParsedPattern)
                isInsideBlock = True
            else:
                if thisParsedPattern == prevParsedPattern and thisParsedIdx == prevParsedIdx + 1:
                    # Continue parsing this block
                    prevParsedIdx = thisParsedIdx
                else:
                    # The block is over
                    isShortened = self._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName) or isShortened
                    firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern = self._startBlock(thisParsedIdx, line, thisParsedPattern)
                    isInsideBlock = True
        
        if isInsideBlock:
            isShortened = self._finishBlock(outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName) or isShortened
        
        return outLines, isShortened
        
    def _startBlock(self, thisParsedIdx, line, thisParsedPattern):
        return thisParsedIdx, thisParsedIdx, line, thisParsedPattern
        
    def _finishBlock(self, outLines, firstParsedIdx, prevParsedIdx, prevLine, prevParsedPattern, idxVarName):
        if prevParsedIdx != firstParsedIdx:
            outLines.append('    for {} = {}, {} {{'.format(idxVarName, firstParsedIdx, prevParsedIdx))
            outLines.append('    ' + prevParsedPattern)
            outLines.append('    }')
            return True
        else:
            outLines.append(prevLine)
            return False
        
    def _wrapInnerCycles(self, lines):
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
        
    def _unwrapInnerCycles(self, lines):
        outLines = []
        for line in lines:
            if '\n' in line:
                newLines = line.split('\n')
                outLines.append(newLines[0])
                newLines = ['    ' + newLine for newLine in newLines[1 :]]
                outLines.extend(newLines)
            else:
                outLines.append(line)
        return outLines
        
    def _rfindExt(self, line, marker, isSecondIteration):
        idx = line.rfind(marker)
        if idx == -1:
            return idx
        if isSecondIteration:
            idx = line.rfind(marker, 0, idx)
        return idx
        