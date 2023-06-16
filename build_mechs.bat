@echo off
pushd "Mechanisms/Astrocyte"
call build_astrocyte_mechs.bat 1
if errorlevel 1 goto label
cd ../Neuron
call build_neuron_mechs.bat 1
:label
popd
pause