These files reproduce Figures 2c-f from Brown et al, 2010 "Virtual
NEURON: a Strategy For Merged Biochemical and Electrophysiological
Modeling".

These models were implemented in NEURON by Sherry-Ann Brown in the
laboratory of Leslie M. Loew, to whom questions should be addressed.

Usage:
1. Unzip purkinje_ppr.zip into an empty directory.
2. Compile the mod files with mknrndll.
3. To reproduce results for the full model shown in Figures 2c and 2e,
double click on mosinit_spine and spine neck at spinydendrite133.hoc,
or execute nrngui mosinit_spine and spine neck at spinydendrite133.hoc
from the command line.
4. Panels will appear with labeled buttons that allow you to run the
simulation. Click on Init&Run to start the simulation. Voltage plots
will appear in the panels for the soma ("v."), spine, and a spiny
dendrite.
5. To reproduce results for the PPR model shown in Figures 2d and 2f,
double click on mosinit_reduced_PPR model.hoc, or execute nrngui
mosinit_reduced_PPR model.hoc from the command line.
6. Panels will appear with labeled buttons that allow you to run the
simulation. Click on Init&Run to start the simulation. Voltage plots
will appear in the panels for the soma ("v."), spine, and various
portions of dendrites.
7. To explore the PPR model using CVODE or other variable step
solvers, double click on mosinit_reduced_PPR model_cvode.hoc, or
execute nrngui mosinit_reduced_PPR model_cvode.hoc from the command
line.
8. Panels will appear with labeled buttons that allow you to run the
simulation. Click on Init&Run to start the simulation. Voltage plots
will appear in the pan els for the soma ("v."), spine, and various
portions of dendrites.

To reproduce Virtual Cell results for the PPR model shown in Figure 4
and some of the subsequent figures:

This model and all simulations can be accessed as a "Shared
BioModel" by logging in to VCell at http://www.vcell.org; the model
is entitled "Brown et al 2010 Purkinje MultiCompartmental Combined
Biochem and Electrophysiol" under the username Brown.

20111027 ModelDB Administrator: the two files KMcvode.mod Khhcvode.mod
had their integration methods changed from euler to cnexp.  See
http://www.neuron.yale.edu/phpBB/viewtopic.php?f=28&t=592
20120330 NaPcvode, NaFcvode, Khcvode, KDcvode, KC3cvode, KAcvode,
K23cvode, CaTcvode, CaP2cvode, CaEcvode were switched from euler to
cnexp and CalciumP.mod (with cad suffix) was switched from euler to
derivimplicit.  See above NEURON forum link. The 
purkinje_reduced_PPR model.ses and 
purkinje_spine and spine neck at spinydendrite133.ses
files had dt changed from 0.00025 to 0.0025 which is now fairly
converged.
