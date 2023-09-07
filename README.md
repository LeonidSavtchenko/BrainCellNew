# BRAINCELL
## 24/02/2023


<b> BRAINCELL 1.0 </b> Interactive realistic model of brain cells. NEURON/Python environment
<!-- This is adding a picturet -->
<!--![Brain Cell](https://github.com/LeonidSavtchenko/BrainCellNew/blob/main/2696937247-astrocyte.jpg)-->

<p align="center">
<img src="https://github.com/LeonidSavtchenko/BrainCellNew/blob/main/2696937247-astrocyte.jpg" alt="Brain Cell" width=200 height=200 style="display:block; margin:auto;"/>
</p>

<p align="justify" >
BRAINCELL: The ultimate software for modeling and simulating brain cells.

With BRAINCELL, you can create realistic and interactive models of neurons, synapses, and networks. You can explore the dynamics of brain activity, test hypotheses, and discover new insights. Whether you are a researcher, a student, or a curious mind, Brainiac is the software for you.

BRAINCELL: The software that makes your brain cells work smarter
</p>
## Version 1.0

<p align="justify" >
Welcome to our software <b>"BRAINCELL 1.0"</b> that simulates realistic brain cells including astrocytes and neurons! 
This powerful tool is designed to help researchers, neuroscientists, and medical professionals better understand how the brain works and how it responds to various stimuli and treatments.
With our software, you can create detailed simulations of individual neurons and astrocytes with detail nano-geometry  that accurately replicate the complex dynamics of the brain. 
</p>

<p align="justify" >
Our software provides a comprehensive suite of features that enable you to design, run, and analyze simulations of brain cells with ease.
Whether you are a seasoned researcher or a newcomer to the field of neuroscience, our software is easy to use and provides a wide range of customization options. 
You can adjust parameters such as membrane capacitance, ion conductance, and synaptic strength with different spatial distributions and stochastic parameters, and observe the resulting behavior of your simulated cells.
The user manual that accompanies our software is designed to provide you with all the information you need to get started with your simulations. 
It covers topics such as installation and setup, creating and configuring cells and networks, and running simulations and analyzing results.
We are confident that our software will help you unlock new insights into the workings of the brain, and we are committed to providing ongoing support to ensure that you get the most out of your simulations. If you have any questions or need assistance, please do not hesitate to contact our support team.
Thank you for choosing <b>"BRAINCELL"</b>, and we look forward to seeing the exciting discoveries you make using it!

</p>




<!DOCTYPE html>
<html>
  <head>
    <h2>Building a Realistic Cell Model</h2>
  </head>
  <body>
    <h2>The following section describes which experiment data or approximations are preferred when building a realistic cell model.</h2>
    <ol>
      <li>A 3D reconstructed tree of main identifiable cell processes importable from <a href="https://neuromorpho.org/">https://neuromorpho.org/</a> in any format. Alternatively, this could be an artificially generated cell arbour with the branching pattern and branch diameters representing the average (typical) cell from the population of interest.</li>
      <li>Astrocyte nano structures. A sample (20-50) of nanoscopic astroglial processes reconstructed using 3D (serial-section) EM, with rendered surface co-ordinates. This sample will be used to obtain statistical properties of the ultrathin processes to be generated in the model.</li>
	  <li>Neuron nano structures. <b>"BRAINCELL"</b> automatically generates synaptic spines with different distribution densities, geometries, and contacts with synapses. Synapses can be located both on the spines and directly on the dendrites. The user can select all parameters. The user can also control the geometry complexity of the spines. </li>
      <li>Average tissue volume fraction occupied by astroglia and neuron, as distributed radially from the soma to the cell edges. This data set is obtained from two-photon excitation measurements in situ (or from published data).</li>
      <li>The mean membrane surface density and the surface-to-volume fraction values obtained from 3D reconstructions of nanoscopic processes.</li>
      <li>The characteristic I-V curve (somatic patch-clamp, square-pulse current injections) for the cell of interest, other (optional) available functional data such as electrical responses to neurotransitter uncaging or changes in extracellular ion, intracellular calcium wave speed, etc.</li>
    </ol>
	
<h2>Installation</h2>

<h3>System Requirements for <b>"BRAINCELL"</b>:</h3>
<ul>
  <li>The basic languages: C++, MATLAB not older than 2013, and Neuron 7.0</li>
  <li>Platform: Linux or Windows</li>
  <li>Type of operation: Sequential and parallel (MPI) computing</li>
</ul>

<h2>Setting up and running <b>"BRAINCELL"</b>: Main regimes of modelling</h2>

<ol>
  <li>
    <h4>Constructing cell morphology ('Nano-geometry', Host computer only required)</h4>
    <p>Importing the 3D main-branch morphology of cell from <a href="https://neuromorpho.org/">https://neuromorpho.org/</a> into BrainCell; generating, within the NEURON environment, the nanoscopic cell protrusions that reflect experimental data. This regime can be run separately from other parts of <b>"BRAINCELL"</b>, it requires a Host computer with MATLAB (2012 or later) and NEURON (7.2 or later, <a href="https://neuron.yale.edu/neuron/download">https://neuron.yale.edu/neuron/download</a>) installed under Windows 7 or 10.</p>
  </li>
  
  <li>
    <h4>NEURON-based simulations of membrane mechanisms ('NEURON simulations', Host computer only required)</h4>
    <p>Further adjustment of the <b>"BRAINCELL"</b> morphology (in accord with volumetric data); populating the cell with membrane mechanisms; setting up simulation configurations and protocols.  This regime can be run separately from other parts of <b>"BRAINCELL"</b>, it requires a Host computer with MATLAB (2012 or later) and NEURON (7.2 or later, <a href="https://neuron.yale.edu/neuron/download">https://neuron.yale.edu/neuron/download</a>) installed under Windows 7 or 10.</p>
  </li>
  
  <li>
    <h4>Simulating full-scale intracellular and extracellular ionic dynamics </h4>
    <p>Design and simulations of longer-term (seconds to minutes) intracellular and extracellular different ionic dynamics within realistic geometry using the cluster / cloud-based parallel computing.  This regime can be run separately from other parts of <b>"BRAINCELL"</b>, it requires a Host computer with MATLAB (2012 or later) and NEURON (7.2 or later, <a href="https://neuron.yale.edu/neuron/download">https://neuron.yale.edu/neuron/download</a>) installed under Windows 7 or 10, and Worker computer / cluster operating under Linux and with preinstalled NEURON (<a href="https://neuron.yale.edu/neuron/download/compile_linux">https://neuron.yale.edu/neuron/download/compile_linux</a>) and MPI.</p>
    <p>Briefly, in this regime, the user working on the Host computer with MATLAB creates a MAT-file containing instructions for computation; uploads this file to the Worker cluster and launches there the simulations  dynamics (independently of the Host computer). The Host computer connects intermittently to the Worker time (a) to monitor computation progress, and (b) to download intermediate simulation results that are displayed and saved in MATLAB. Once simulations have been completed

<section>
      <h2>Documentation</h2>
      <p>Manual and API documentation can be found at <a href="https://github.com/LeonidSavtchenko/BrainCellNew">https://github.com/LeonidSavtchenko/BrainCellNew</a>.</p>
    </section>
    <section>
      <h2>Contact Information</h2>
      <address>
        Written by <a href="mailto:savtchenko#yahoo.com">Dr. Leonid Savtchenko</a>.<br> and Prof. Dmitri Rusakov<br>
        Visit us at:<br>
        <a href="http://www.ucl.ac.uk/ion/departments/epilepsy/themes/synaptic-imaging">Department of Clinical and Experimental Epilepsy<br>Institute of Neurology<br>University College London<br>UK</a>
      </address>
    </section>
  </body>
</html>
