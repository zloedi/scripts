set "var=%1"
set "var=%var:\=\\%"
rem echo %var%
rem PAUSE
C:\cygwin64\bin\mintty.exe /bin/bash --login -c "vim $(cygpath -u '%var%')"

