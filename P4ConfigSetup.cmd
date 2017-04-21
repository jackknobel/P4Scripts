@echo off

:: %~dp0 is the path to the batch file
set WorkspaceRoot=%CD%
set ConfigFile="%WorkspaceRoot%\p4config.txt"

:: Clear our old file
break>%ConfigFile%

echo Setting up Perforce for first time use

:: Set our port number
echo Enter the port number. Should be along the lines of IP/Host:PortNumber
set /p port="Port: "
echo P4PORT=%port% >> %ConfigFile%

echo:

:: Set our P4Host
set Host=""

: HostQuestion
SET /P ANSWER="Use PC name as P4Host? (Y/N) "

IF /i "%ANSWER%" EQU "Y" goto AcquireHostName
IF /i "%ANSWER%" EQU "N" goto ManuallySet

echo Invalid Response
goto HostQuestion

: AcquireHostName 
set Host=%ComputerName%
goto Continue

: ManuallySet
set /p Host="Enter Host: "
goto Continue

: Continue
echo Hostname set to %Host%
echo P4HOST=%Host% >> %ConfigFile%

echo:

:: Get User input for this one
set /p id="Enter Username: "
echo P4USER=%id% >> %ConfigFile%
echo P4CHARSET=utf8 >> %ConfigFile%

p4 set P4CONFIG=%ConfigFile%

echo:

:: Copy our port number to the clipboard for easy copy paste
echo %port% Copied to the Clipboard!
echo %port%| clip

:: Wait to make it look like something is happening
TIMEOUT /t 1 /nobreak>nul

echo:

echo Lauching P4V
start p4v