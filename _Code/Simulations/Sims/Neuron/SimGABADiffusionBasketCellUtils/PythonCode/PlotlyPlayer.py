
# !!! BUGs:
#     * the markers for distant points are shown in front of the markers for close points
#     * the markers don't change their size on scaling the scene
#     * too many ticks on the slider for real records
#     * the garbage in the last digits of the label "t (ms)=..." and the slider tick labels

# https://plotly.com/python/3d-scatter-plots/
# https://plotly.com/python/animations/

import plotly.express as px
import pandas as pd
import numpy as np


class PlotlyPlayer:
    
    _markerSize = 20
    _opacity = 0.5
    _palette = 'viridis'
    
    
    _fig = None
    
    
    def __init__(self, x, y, z, rangeVar, t, numSegms, numFrames, varNameWithIndexAndUnits):
        
        data = {
            'x (μm)': np.concatenate([x] * numFrames),
            'y (μm)': np.concatenate([y] * numFrames),
            'z (μm)': np.concatenate([z] * numFrames),
            varNameWithIndexAndUnits: rangeVar,
            't (ms)': np.repeat(t, numSegms)
        }
        df = pd.DataFrame(data)
        
        # Create a 3D scatter plot with Plotly
        self._fig = px.scatter_3d(df, x='x (μm)', y='y (μm)', z='z (μm)', color=varNameWithIndexAndUnits, animation_frame='t (ms)', color_continuous_scale=self._palette, opacity=self._opacity)
        
        # Update the marker size
        self._fig.update_traces(marker=dict(size=self._markerSize))
        
        # Customize the axis labels
        self._fig.update_layout(scene=dict(xaxis_title='x (μm)', yaxis_title='y (μm)', zaxis_title='z (μm)'))
        
        # Set the aspect ratio to 'data' to preserve proportions
        self._fig.update_scenes(aspectmode='data')
        
        # Customize the colour bar
        color_min = rangeVar.min()  # !!! maybe round these values
        color_max = rangeVar.max()  #
        self._fig.update_coloraxes(cmin=color_min, cmax=color_max, colorbar_title=varNameWithIndexAndUnits)
        
        # Customize the figure and subplot titles
        self._fig.update_layout(title=varNameWithIndexAndUnits)
        
    def show(self):
        
        # Show the Plotly figure
        self._fig.show()
        