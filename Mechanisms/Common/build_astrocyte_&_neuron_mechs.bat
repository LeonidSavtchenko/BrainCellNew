@echo off

set isBuildMechsForAstrocyte=%1
set isBuildMechsForNeuron=%2

if not "%isBuildMechsForAstrocyte%" == "0" (
    call :buildMechsForThisCellType Astrocyte
)
if errorlevel 1 goto label1
if not "%isBuildMechsForNeuron%" == "0" (
    call :buildMechsForThisCellType Neuron
)
:label1
if "%1" == "" pause
goto :eof

:buildMechsForThisCellType
    set cellTypeFolderName=%1
    set "modFilesFolderName=MOD files"
    set tempFolderName=temp_folder
    pushd ..
    if exist %tempFolderName% (
        rmdir %tempFolderName% /S /Q
    )
    mkdir %tempFolderName%
    cd %tempFolderName%
    echo.
    xcopy "..\Common\%modFilesFolderName%\*" /Q
    xcopy "..\%cellTypeFolderName%\%modFilesFolderName%\*" /Q
    echo.
    echo     Building %cellTypeFolderName% mechs ...
    echo.
    call "C:\nrn\bin\mknrndll.bat"
    echo.
    rem "mknrndll.bat" does not set %errorlevel% to 1 on error,
    rem so we have to rely on %errorlevel% set by "move" command below
    copy nrnmech.dll "..\..\Nanogeometry\%cellTypeFolderName%\"
    move nrnmech.dll "..\%cellTypeFolderName%\"
    echo.
    if errorlevel 1 goto label2
        cd ..
        rmdir %tempFolderName% /S /Q
    :label2
    popd
    goto :eof
    