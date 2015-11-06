rem checkout.bat

echo off

rem Checkout the synApps trunk from the subversion repository

mkdir synAppsSVN
cd synAppsSVN

rem For file access
rem set APS_SVN=file:///home/joule/SVNSYNAP/svn

rem For https access
set APS_SVN=https://subversion.xray.aps.anl.gov/synApps
set GIT_BASE=https://github.com

svn co %APS_SVN%/support/trunk support
cd support

set aps_items=      
set git_drivers=
set git_admin=

set aps_items=%aps_items% ebrick
set aps_items=%aps_items% optics
set aps_items=%aps_items% softGlue
set aps_items=%aps_items% sscan
set aps_items=%aps_items% stream
set aps_items=%aps_items% xxx

set git_drivers=%git_drivers% alive
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
set git_drivers=%git_drivers% motor
set git_drivers=%git_drivers% quadEM
set git_drivers=%git_drivers% std
set git_drivers=%git_drivers% vac
set git_drivers=%git_drivers% vme

set git_admin=%git_admin% configure
set git_admin=%git_admin% documentation
set git_admin=%git_admin% utils

FOR %%i IN (%git_admin%) DO svn co %GIT_BASE%/EPICS-synApps/%%i/trunk %%i
FOR %%i IN (%git_drivers%) DO svn co %GIT_BASE%/epics-modules/%%i/trunk %%i
FOR %%i IN (%aps_items%) DO svn co %APS_SVN%/%%i/trunk %%i
