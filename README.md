# BRAINCELL 1.0 - Modeling and Simulating Brain Cells
*Explore the Wonders of the Brain*

<p align="center">
<img src="https://github.com/LeonidSavtchenko/BrainCellNew/blob/main/2696937247-astrocyte.jpg" alt="Brain Cell" width=200 height=200 style="display:block; margin:auto;"/>
</p>

Welcome to **BRAINCELL 1.0**, your gateway to understanding the intricate world of brain cells. This cutting-edge software empowers researchers, neuroscientists, and medical professionals to explore the brain's inner workings, reactions to stimuli, and responses to treatments. With **BRAINCELL 1.0**, you can create lifelike simulations of neurons and astrocytes with nano-geometry precision, faithfully replicating the brain's complex dynamics.

# Installation

## Key System and Software Requirements

To ensure a smooth experience with BrainCell, please make sure your system meets the following requirements:

1. **PYTHON** (version 3.2 or later) -  [Python Downloads](https://www.python.org/downloads/)
2. **NEURON** (version 7.2 or later) -  [NEURON Downloads](https://neuron.yale.edu/neuron/download)
3. Installed Neuron on Windows.



# Preparing BRAINCELL System Files

## Step 1: Update File Properties for Windows 11 Users
For Windows 11 users, ensure that any `*.exe` file in the NEURON directory, specifically located at `c:\nrn\bin\`, operates with administrative rights. However, for users with a version of Windows < 11, this step is not required. To achieve this, follow the steps outlined below:
- Updating File Properties: Navigate to the NEURON directory `c:\nrn\bin\` and locate the `*.exe` files. Adjust the properties of each `*.exe` file according to the guidelines presented in the image below.

## Step 2: Execute the init.hoc File
Run the `init.hoc` file from the host computer directory. You can find this file in the directory path `...\init.hoc`. Alternatively, you can use the 'NEURON simulations' button accessible from the start menu panel.

## Step 3: Compile NEURON .mod Files
Activate `build_mechs.bat` to initiate the compilation of NEURON `*.mod` files. This step is crucial for proper functioning and integration of the NEURON modules into your system.

By following these steps, you'll ensure the seamless operation and effective compilation of NEURON files, enabling you to utilize NEURON functionalities efficiently.

## Step 4: Run Scripts on Windows
If your Windows configuration restricts the execution of batch (bat) files, you can opt to run PowerShell (ps1) files instead. Windows, by default, imposes restrictions on the execution of PS1 files. To overcome this limitation, follow the steps below:
- Open PowerShell in administrator mode.
- Run the following command:
    ```
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
    ```
  This command bypasses the execution policy for the current user, allowing PS1 files to run without restrictions.
  This action is a one-time requirement; you will not need to repeat it in the future. After performing this step, you can effortlessly run PS1 files under PowerShell by right-clicking on the file and selecting the following command:


This ensures smooth execution of PowerShell scripts for enhanced efficiency.

## Step 5: Running BrainCell
- Open the `c:\my\braincell` directory.
- Double-click on the `init.bat` file to execute it.
- This action should launch Neuron and open the BRAINCELL window.
- In the BRAINCELL window, you can select either "Astrocyte" or "Neuron" per your requirements.



# Setting Up and Running BRAINCELL
### 1. Constructing Cell Morphology (Nano-geometry)
- Import the 3D main-branch morphology of cells from [neuromorpho.org](https://neuromorpho.org/).
- Generate nanoscopic cell protrusions within the NEURON environment.

# Key Features
- **Realistic Cell Models**: Create detailed simulations of individual neurons and astrocytes with nano-geometry accuracy.
- **Customizable Parameters**: Adjust membrane capacitance, ion conductance, synaptic strength, and more, observing how these changes affect cell behavior.
- **User-Friendly Interface**: Designed for both seasoned researchers and newcomers, our software is easy to use and offers extensive customization options.
- **Comprehensive Documentation**: Our user manual covers installation, setup, simulation creation, and result analysis to help you get started.
- **Ongoing Support**: We're committed to assisting you in unlocking new insights into brain function.

# Building Realistic Cell Models
When building a realistic cell model, consider the following essential elements:
1. **Cell Processes**: Import a 3D reconstructed tree of main cell processes from [neuromorpho.org](https://neuromorpho.org/) or generate artificial cell arbors.
2. **Astrocyte Nanostructures**: Reconstruct nanoscopic astroglial processes for statistical properties.
3. **Neuron Nanostructures**: Our software automatically generates synaptic spines with customizable parameters.
4. **Tissue Volume Fraction**: Determine the volume fraction occupied by astroglia and neurons, considering radial distribution from the soma.
5. **Membrane Surface Density**: Utilize 3D reconstructions of nanoscopic processes.
6. **Functional Data**: Include data like I-V curves, electrical responses, and intracellular calcium wave speed.



### 2. NEURON-Based Simulations of Membrane Mechanisms
- Refine cell morphology based on volumetric data.
- Populate cells with membrane mechanisms.
- Configure simulations and protocols.

### 3. Simulating Ionic Dynamics
- Design and simulate intracellular and extracellular ionic dynamics.
- Use cluster/cloud-based parallel computing for longer-term simulations.

Documentation and API details can be found [here](https://github.com/LeonidSavtchenko/BrainCellNew).

## Contact Information
- **Dr. Leonid Savtchenko**: [Email](mailto:savtchenko#yahoo.com)
- **Prof. Dmitri Rusakov**
- Visit us at:
  [Department of Clinical and Experimental Epilepsy](http://www.ucl.ac.uk/ion/departments/epilepsy/themes/synaptic-imaging)
  
-  Institute of Neurology
-  University College London, UK