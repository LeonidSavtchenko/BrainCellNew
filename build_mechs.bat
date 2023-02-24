@echo off
cd Mechanisms
call "C:\nrn\bin\mknrndll.bat"
del *.c
del *.o
move nrnmech.dll ..\
pause