# BRAINCELL
## 24/02/2023


BRAINCELL 1.0. Interactive realistic model of brain cells. NEURON/Python environment

## Version 1.0

<p> 

Welcome to our software "BRAINCELL 1.0" that simulates realistic brain cells including astrocytes and neurons! 
This powerful tool is designed to help researchers, neuroscientists, and medical professionals better understand how the brain works and how it responds to various stimuli and treatments.
With our software, you can create detailed simulations of individual neurons and astrocytes with detail nano-geometry  that accurately replicate the complex dynamics of the brain. 
</p>
<p>
Our software provides a comprehensive suite of features that enable you to design, run, and analyze simulations of brain cells with ease.
Whether you are a seasoned researcher or a newcomer to the field of neuroscience, our software is easy to use and provides a wide range of customization options. 
You can adjust parameters such as membrane capacitance, ion conductance, and synaptic strength with different spatial distributions and stochastic parameters, and observe the resulting behavior of your simulated cells.
The user manual that accompanies our software is designed to provide you with all the information you need to get started with your simulations. 
It covers topics such as installation and setup, creating and configuring cells and networks, and running simulations and analyzing results.
We are confident that our software will help you unlock new insights into the workings of the brain, and we are committed to providing ongoing support to ensure that you get the most out of your simulations. If you have any questions or need assistance, please do not hesitate to contact our support team.
Thank you for choosing "BRAINCELL", and we look forward to seeing the exciting discoveries you make using it!

</p>




## Experimental data or estimates desirable to build a realistic cell  model

##### 1. A 3D reconstructed tree of main identifiable cell processes importable into NEURON. Alternatively, this could be 
#####    an artificially generated cell arbour with the branching pattern and branch diameters representing the average (typical)  cell from the population of interest. 
##### 2. A sample (20-50) of nanoscopic astroglial processes and neuron spines reconstructed using 3D (serial-section) EM, with rendered surface co-ordinates. 
#####    This sample will be used to obtain statistical properties of the ultrathin processes to be generated in the model. 
##### 3. Average tissue volume fraction occupied by astroglia and neuron, as distributed radially from the soma to the cell edges. 
#####    This data set is obtained from two-photon excitation measurements in situ (or from published data). 
##### 4. The mean membrane surface density and the surface-to-volume fraction values obtained from 3D reconstructions of nanoscopic  processes.  
##### 5. The characteristic I-V curve (somatic patch-clamp, square-pulse current injections) for the cell of interest, other (optional) available functional data such as electrical responses to glutamate uncaging or changes in extracellular potassium, intracellular calcium wave speed, etc. 


## Installation. 

### System Requirements for BRAINCELL:
#### •	The basic languages : C++, MATLAB not older 2013 and Neuron 7.0
#### •	Platform : Linux and Windows. 
#### •	Type of operation : Sequential and parallel (MPI) computing


## Setting up and running BRAINCELL: Main regimes of modelling 


##### 1.	Constructing astroglial morphology ('Nano-geometry', Host computer only required). Importing the 3D main-branch morphology of astroglia into NEURON; generating, within the NEURON environment, the nanoscopic astroglial protrusions that reflect experimental data. This regime can be run separately from other parts of ASTRO, it requires a Host computer with MATLAB (2012 or later) and NEURON (7.2 or later, https://neuron.yale.edu/neuron/download) installed under Windows 7 or 10. 

##### 2.	NEURON-based simulations of membrane mechanisms ('NEURON simulations', Host computer only required). Further adjustment of the astrocyte morphology (in accord with volumetric data); populating the cell with membrane mechanisms; setting up simulation configurations and protocols. This regime can be run separately from other parts of ASTRO, it requires a Host computer with MATLAB (2012 or later) and NEURON (7.2 or later, https://neuron.yale.edu/neuron/download) installed under Windows 7 or 10. 
##### 3.	Simulating full-scale Ca2+ dynamics ('Calcium Dynamics on Cluster', Host and Worker computers normally required). Design and simulations of longer-term (seconds to minutes) intracellular calcium dynamics within realistic geometry using the cluster / cloud-based parallel computing. This regime can be run separately from other parts of ASTRO, it requires a Host computer with MATLAB (2012 or later) and NEURON (7.2 or later, https://neuron.yale.edu/neuron/download) installed under Windows 7 or 10, and Worker computer / cluster operating under Linux and with preinstalled NEURON (https://neuron.yale.edu/neuron/download/compile_linux) and MPI. 
##### Briefly, in this regime, the user working on the Host computer with MATLAB creates a MAT-file containing instructions for computation; uploads this file to the Worker cluster and launches there the simulations of astroglial Ca2+ dynamics (independently of the Host computer). The Host computer connects intermittently to the Worker time (a) to monitor computation progress, and (b) to download intermediate simulation results that are displayed and saved in MATLAB. Once simulations have been completed, the MATLAB module running on the Host computer downloads the output MAT-file and visualises the computation results. 


## Documentation

Manual and API documentation can be found at https://github.com/LeonidSavtchenko/BrainCell



<address>

Written by <a href="mailto:savtchenko#yahoo.com">Dr. Leonid Savtchenko</a>.<br> and Prof. Dmitri Rusakov 
Visit us at:<br>
http://www.ucl.ac.uk/ion/departments/epilepsy/themes/synaptic-imaging <br>
Department of Clinical and Experimental Epilepsy<br>
Institute of Neurology<br>
University College London<br>
UK<br>

</address>
