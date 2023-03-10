
import os
from neuron import h, hoc, nrn


class Generators:
    """!!"""
    
    hocObj = hoc.HocObject()
    
    def getAllCreateStatementsExceptNanogeometry(self):
        """!!input: allNames (List of String-s, taken from the top level)
        output: a string like 'create name1, name2[123], name3[456][7], ...'"""
        
        if len(self.hocObj.allNames) == 0:
            _codeContractViolation()
        
        createdNames = []
        for name in self.hocObj.allNames:
            createdName = name.s
            
            # !! update this logic once I correct\\replace getAllSectionNames which produces allNames
            if createdName == 'AstrocyteNanoBranch' or createdName == 'NeuronNanoBranch':   # !! hardcode
                continue
                
            secObj = self._getHocVar(createdName)
            while True:
                isSecObjOrArray = self._isSecObjOrArray(secObj)
                if isSecObjOrArray:
                    break
                else:
                    createdName += '[{}]'.format(len(secObj))
                    secObj = secObj[0]
                    
            createdNames.append(createdName)
            
        resStr = 'create ' + ', '.join(createdNames)
        
        return resStr
        
    def getIntegerValueFromTopLevel(self, varName):
        return self._generateAssignment(varName, True)
        
    def getDoubleValueFromTopLevel(self, varName):
        return self._generateAssignment(varName, False)
        
    def createListOfSectionRef(self, usedNamesHocListName, secRefHocListName):
        allLines = []
        newLine = '{} = new List()'.format(secRefHocListName)
        allLines.append(newLine)
        for usedNameHocString in self._getHocVar(usedNamesHocListName):
            usedName = usedNameHocString.s
            secObj = self._getHocVar(usedName)
            isSecObjOrArray = self._isSecObjOrArray(secObj)
            if isSecObjOrArray:
                newLine = '{} {}.append(new SectionRef())'.format(usedName, secRefHocListName)
                allLines.append(newLine)
            else:
                newLines = [
                    'for idx = 0, {} - 1 {{'.format(len(secObj)),
                    '    {}[idx] {}.append(new SectionRef())'.format(usedName, secRefHocListName),
                    '}']
                allLines.extend(newLines)
        return allLines
        
    # !! ask Lesha whether to split topology by blocks for soma, dendrites, axon, nanogeometry, other
    def initTopology(self):
        lines = []
        for sec in h.allsec():
            secRef = h.SectionRef(sec)
            if not secRef.has_parent():
                continue
            # Some comments:
            # 1. The syntax "connect child(x), parent(y)" looks simpler than "parent connect child(x), y",
            #    but the former does not work for the sections owned by templates (all nanogeometry in our case)
            # 2. The syntax "sec=sec" is important here; do not replace it with "sec", because the called methods will always return 0
            # 3. Max. precision is applied in the next line by Python automatically
            line = '{} connect {}({}), {}'.format(secRef.parent.name(), sec.name(), h.section_orientation(sec=sec), h.parent_connection(sec=sec))
            lines.append(line)
        return lines
        
    # !! for file "Geometry\Neuron\test.hoc", we have:
    #    AstrocyteNanoBranch[0].SmallGlia[0] { ... pt3dadd(0.075074203312397, -0.07739131152629852, 0.0, 0.10000000149011612
    #    why garbage in diam?
    # !! for file "Geometry\Astrocyte\New Style\AstrocyteBasicGeometry.hoc", we have:
    #    soma[0] { ... pt3dadd(0.23000000417232513, 5.829999923706055, 0.0, 7.22599983215332)
    #    why garbage in x?
    # !! ask Lesha whether to split geometry by blocks for soma, dendrites, axon, nanogeometry, other
    # !! investigate at which stage of the program the 3D-coordinates of 1st point of 1st imported dendrite become changed (at least in the next files: AstrocyteBasicGeometry.hoc и cellmorphology.hoc)
    #    "connect" command does not change them, so maybe finitialize?
    def initGeometry(self):
        lines = []
        for sec in h.allsec():
            line = '{} {{'.format(sec.name())
            lines.append(line)
            lines.append('    pt3dclear()') # Almost sure that not needed, but Cell Builder's Exporter adds this
            for ptIdx in range(sec.n3d()):
                # Max. precision is applied here automatically
                line = '    pt3dadd({}, {}, {}, {})'.format(sec.x3d(ptIdx), sec.y3d(ptIdx), sec.z3d(ptIdx), sec.diam3d(ptIdx))
                lines.append(line)
            if sec.nseg != 1:
                line = '    nseg = {}'.format(sec.nseg)
                lines.append(line)
            lines.append('}')
        return lines
        
    def insertAllLinesFromFile(self, relFilePathName):
        absFilePathName = os.getcwd() + '\\' + relFilePathName
        with open(absFilePathName, 'r') as inFile:
            inText = inFile.read()
        return inText.splitlines()  # Removing all newline characters here
    
    def _getHocVar(self, varName):
        """!!"""
        return eval('self.hocObj.' + varName)   # !! maybe can do it via refletion
        
    def _generateAssignment(self, varName, isIntegerOrDouble):
        value = self._getHocVar(varName)
        if isIntegerOrDouble:
            value = int(value)
        return '{} = {}'.format(varName, value)
        
    def _isSecObjOrArray(self, secObj):
        """!!"""
        tp = type(secObj)
        # !! can I use switch here?
        if tp == nrn.Section:
            return 1
        elif tp == hoc.HocObject:
            return 0
        else:
            _codeContractViolation()
            