@echo off
pushd "MOD files"
echo.
echo     Building Neuron mechs ...
echo.
call "C:\nrn\bin\mknrndll.bat"
rem "mknrndll.bat" does not set %errorlevel% to 1 on error,
rem so we have to rely on %errorlevel% set by "move" command below
echo.
copy nrnmech.dll ..\..\..\Nanogeometry\Neuron\
move nrnmech.dll ..\
if errorlevel 1 goto label
del *.c
del *.o
rem "*.tmp" files remain only after (previous) unsuccessful builds
del *.tmp >nul 2>&1
:label
echo.
popd
if "%1" == "" pause