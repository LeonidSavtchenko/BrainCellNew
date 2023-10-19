NEURON mod files from the paper:
S. Watanabe, D.A. Hoffman, M. Migliore, and D. Johnston
Dendritic K+ channels contribute to spike-timing dependent 
long-term potentiation in hippocampal pyramidal neurons 
Proc.Natl.Acad.Sci. USA 99:8366-8371, 2002.

The fig6.hoc simulation file will show the membrane potential
in a distal dendrite (350um from soma) for three simulations,
as in Fig.6 of the paper.
In each case two APs are elicited, unpaired with EPSPs
or paired with EPSPs after a 35 or 45ms delay.
The simulations show that the APs in the dendrites are boosted
only when they are paired with coincident EPSPs. 

Under unix systems:
to compile the mod files use the command 
nrnivmodl 
and run the simulation hoc file with the command 
nrngui fig6.hoc

Under Windows systems:
to compile the mod files use the "mknrndll" command.
A double click on the simulation file
fig6.hoc 
will open the simulation window.

Questions on how to use this model with NEURON
should be directed to michele.migliore@pa.ibf.cnr.it