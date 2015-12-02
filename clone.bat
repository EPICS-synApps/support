rem checkout.bat

echo off

rem clone all the synApps modules from GitHub

mkdir synAppsGIT
cd synAppsGIT

set GIT_BASE=https://github.com

rem clone the main synApps/support
git clone %GIT_BASE%/EPICS-synApps/support
cd support

set git_drivers=
set git_admin=

set git_drivers=%git_drivers% alive
set git_drivers=%git_drivers% asyn
set git_drivers=%git_drivers% autosave
set git_drivers=%git_drivers% busy
set git_drivers=%git_drivers% calc
set git_drivers=%git_drivers% camac
set git_drivers=%git_drivers% caputRecorder
set git_drivers=%git_drivers% dac128V   
set git_drivers=%git_drivers% delaygen
set git_drivers=%git_drivers% dxp
set git_drivers=%git_drivers% ip
set git_drivers=%git_drivers% ip330
set git_drivers=%git_drivers% ipUnidig
set git_drivers=%git_drivers% love
set git_drivers=%git_drivers% mca
set git_drivers=%git_drivers% measComp
set git_drivers=%git_drivers% modbus
set git_drivers=%git_drivers% optics
set git_drivers=%git_drivers% motor
set git_drivers=%git_drivers% quadEM
set git_drivers=%git_drivers% softGlue
set git_drivers=%git_drivers% sscan
set git_drivers=%git_drivers% std
set git_drivers=%git_drivers% stream
set git_drivers=%git_drivers% vac
set git_drivers=%git_drivers% vme
set git_drivers=%git_drivers% xxx

set git_admin=%git_admin% configure
set git_admin=%git_admin% documentation
set git_admin=%git_admin% utils

FOR %%i IN (%git_admin%) DO git clone %GIT_BASE%/EPICS-synApps/%%i.git
FOR %%i IN (%git_drivers%) DO git clone %GIT_BASE%/epics-modules/%%i.git
git clone --recursive https://github.com/areaDetector/areaDetector.git
