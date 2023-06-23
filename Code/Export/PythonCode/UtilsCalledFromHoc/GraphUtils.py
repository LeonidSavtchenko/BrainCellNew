
import os, shutil
from neuron import h
from Utils.OtherUtils import codeContractViolation


class GraphUtils:
    
    # This method is just a workaround to achieve what cannot be done in NEURON directly.
    # Looking forward to delete it in favour of smth simple like Graph.getAllVars once NEURON has such a method.
    # The code below works fine in NEURON 8.2.2, but there is no guarantee for the future versions.
    @classmethod
    def parseVarsFromTheGraph(cls, varsList):
        
        tempFolderPath = 'Code\\Export\\temp_folder'
        sesFileName = 'last_session.ses'
        
        cls._createOrCleanUpTempFolder(tempFolderPath)
        
        sesFilePath = os.path.join(tempFolderPath, sesFileName)
        h.save_session(sesFilePath)
        
        # Find a particular Graph, then parse its vars
        isStartFound = 0
        isEndFound = 0
        with open(sesFilePath, 'r') as file:
            for line in file:
                if not isStartFound:
                    # Keep the var name in sync with CreateListOfOutputVarsWidget.show
                    if line.startswith('someUniqueNameForTheParsedGraph = '):
                        isStartFound = 1
                else:
                    # It turns out, NEURON saves the same variable using "addvar" or "addexpr" depending on
                    # how it was chosen by user in "Plot what?" widget:
                    # * Double click in the second list, then "Accept" => "addvar"
                    # * Single click in the second list, then "Accept" => "addexpr"
                    if '.addvar(' in line or '.addexpr(' in line:
                        startIdx = line.index('"') + 1
                        endIdx = line.index('"', startIdx)
                        varStr = line[startIdx : endIdx]
                        varsList.append(h.String(varStr))
                    elif line.startswith('}'):
                        isEndFound = 1
                        break
                        
        if not isStartFound or not isEndFound:
            codeContractViolation()
            
        shutil.rmtree(tempFolderPath)
        
        
    def _createOrCleanUpTempFolder(tempFolderPath):
        if os.path.exists(tempFolderPath):
            for fileName in os.listdir(tempFolderPath):
                filePath = os.path.join(tempFolderPath, fileName)
                os.remove(filePath)
        else:
            os.mkdir(tempFolderPath)
            