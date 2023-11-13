
# !!! Ideas:
#     * think about the usage of log colourbar (if supported) or explicit expressions for the watched var, e.g. "log(gabao)"
#     * maybe make "z" axis normal to the screen by default to be consistent with PlotShape default view direction
#     * maybe cache data in Python to make the wait time for "Show the last record once again" shorter

from PlotlyPlayer import PlotlyPlayer
from PyplotPlayer import PyplotPlayer

import numpy as np
from neuron import h
from OtherInterModularUtils import codeContractViolation


class RangeVarAnimationPlayer:
    
    _record = None
    
    
    def __init__(self, record):
        self._record = record
        
    def play(self, frontEndIdx, isTestMode):
        
        h.mwh.showPleaseWaitBox('Preparing animation.')
        
        varNameWithIndexAndUnits = self._record.varNameWithIndexAndUnits
        
        # 3D coordinates of segment centres
        x = self._record.xVec
        y = self._record.yVec
        z = self._record.zVec
        
        # The time grid
        t = self._record.timeVec
        
        numSegms = len(x)
        numFrames = len(t)
        
        if frontEndIdx == 0:
            
            if isTestMode:
                # !!! just some random test data here
                rangeVar = np.random.rand(numSegms * numFrames)
            else:
                # !!! would it give any benefit converting NEURON Vector rangeVar to NumPy array here? (see Vector.to_python)
                rangeVar = self._record.rangeVarVec
                
            player = PlotlyPlayer(x, y, z, rangeVar, t, numSegms, numFrames, varNameWithIndexAndUnits)
            
        elif frontEndIdx == 1 or frontEndIdx == 2:
            
            if isTestMode:
                # !!! just some random test data here
                rangeVar = np.random.rand(numFrames, numSegms)
            else:
                rangeVar = np.empty(numSegms * numFrames)
                self._record.rangeVarVec.to_python(rangeVar)
                rangeVar = np.reshape(rangeVar, (numFrames, numSegms))
                
            isDesktopOrBrowser = 2 - frontEndIdx
            player = PyplotPlayer(x, y, z, rangeVar, numFrames, isDesktopOrBrowser, varNameWithIndexAndUnits)
            
        else:
            codeContractViolation()
            
        h.mwh.hidePleaseWaitBox()
        
        player.show()
        