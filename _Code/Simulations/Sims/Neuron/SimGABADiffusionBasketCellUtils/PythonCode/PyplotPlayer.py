
# !!! BUGs:
#     * when rotating the scene, the points disappear randomly
#     * when clicking "Start", it starts from the place where we stopped rather than from the current frame selected with the slider
#     * when creating the second animation using "Pyplot (desktop)" front end, it stops shortly, the button and the slider become unresponsive and the next message is printed to console:
#           QCoreApplication::exec: The event loop is already running

# https://matplotlib.org/stable/gallery/animation/random_walk.html

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider
import webbrowser
import numpy as np


class PyplotPlayer:
    
    _markerSize = 200
    _animationEmbedLimit = 300  # MB    # For browser mode only
    _tempHtmlFileName = 'temp.html'     #
    
    _isUseOpacitiesOrColours = True
    _markerColour = 'c'     # Used only when the flag above is True
    _palette = 'viridis'    # Used only when the flag above is False
    
    
    _isDesktopOrBrowser = None
    _rangeVar = None
    _scatter = None
    _button = None
    _slider = None
    _ani = None
    _isRunning = True
    _isProgrammaticSliderChange = False
    
    
    def __init__(self, x, y, z, rangeVar, numFrames, isDesktopOrBrowser, varNameWithIndexAndUnits):
        
        if self._isUseOpacitiesOrColours:
            rangeVar_min = rangeVar.min()       # !!! use the base concentration here, e.g. h.gabao0_gaba_ion
            rangeVar_max = rangeVar.max()
            
            if rangeVar_min > 0:
                # Apply logarithm to prevent domination of the biggest spike
                rangeVar = np.log(rangeVar)
                rangeVar_min = np.log(rangeVar_min)
                rangeVar_max = np.log(rangeVar_max)
                varNameWithIndexAndUnits = 'Log of ' + varNameWithIndexAndUnits
                
            # Scale the data to fit [0, 1] range
            rangeVar = (rangeVar - rangeVar_min) / (rangeVar_max - rangeVar_min)
            
        self._isDesktopOrBrowser = isDesktopOrBrowser
        self._rangeVar = rangeVar
        
        # Create a 3D plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        if self._isUseOpacitiesOrColours:
            # Plot the 3D point cloud
            self._scatter = ax.scatter(x, y, z, alpha=rangeVar[0], s=self._markerSize, c=self._markerColour, linewidths=0)
        else:
            # Create a colormap
            cmap = plt.get_cmap(self._palette)
            
            # Plot the 3D point cloud
            self._scatter = ax.scatter(x, y, z, c=rangeVar[0], cmap=cmap, s=self._markerSize, linewidths=0)
            
            # Add a color bar to indicate the values
            colorBar = plt.colorbar(self._scatter)
            colorBar.ax.set_title(varNameWithIndexAndUnits)
            
        # Set the aspect ratio to be equal (preserve proportions)
        ax.set_aspect('equal')
        
        # Set labels for the axes
        ax.set_xlabel('x (μm)')
        ax.set_ylabel('y (μm)')
        ax.set_zlabel('z (μm)')
        
        fig.suptitle(varNameWithIndexAndUnits)
        
        # !!! use blit=True and update method _onNewFrame when we show the extracellular sources
        self._ani = FuncAnimation(fig, self._onNewFrame, frames=numFrames)
        
        if isDesktopOrBrowser:
            
            # Create a button to start and stop the animation
            ax_button = plt.axes([0.05, 0.125, 0.1, 0.05])
            self._button = Button(ax_button, 'Stop')
            self._button.on_clicked(self._onButtonClick)
            
            # Add a slider for frame selection
            ax_slider = plt.axes([0.1, 0.05, 0.8, 0.05])
            # !!! maybe show "t (ms)" instead of "Frame"
            self._slider = Slider(ax_slider, 'Frame', valmin=0, valmax=numFrames - 1, valstep=1)
            self._slider.on_changed(self._onSliderChange)
        else:
            
            # Increase the animation size limit
            plt.rcParams['animation.embed_limit'] = self._animationEmbedLimit
            
            html = self._ani.to_jshtml()
            
            # Save the HTML string to a temporary HTML file
            with open(self._tempHtmlFileName, 'w') as f:
                f.write(html)
                
    def show(self):
        if self._isDesktopOrBrowser:
            plt.show()
        else:
            # Open the temporary HTML file in the default web browser
            webbrowser.open(self._tempHtmlFileName)
            
            
    def _onNewFrame(self, frameIdx):
        self._setOpacitiesOrColours(frameIdx)
        
        if not self._isDesktopOrBrowser:
            return
            
        self._isProgrammaticSliderChange = True
        self._slider.set_val(frameIdx)
        self._isProgrammaticSliderChange = False
        
    def _onButtonClick(self, _):
        if self._isRunning:
            self._ani.event_source.stop()
            self._button.label.set_text('Start')
        else:
            self._ani.event_source.start()
            self._button.label.set_text('Stop')
        self._isRunning = not self._isRunning
        
        # Refresh the button text
        plt.draw()
        
    def _onSliderChange(self, val):
        if self._isProgrammaticSliderChange:
            return
            
        frameIdx = int(val)
        self._setOpacitiesOrColours(frameIdx)
        
        self._ani.event_source.stop()
        self._button.label.set_text('Start')
        self._isRunning = False
        
        # Refresh the button text
        plt.draw()
        
        
    def _setOpacitiesOrColours(self, frameIdx):
        data = self._rangeVar[frameIdx]
        if self._isUseOpacitiesOrColours:
            self._scatter.set_alpha(data)
        else:
            self._scatter.set_array(data)
            