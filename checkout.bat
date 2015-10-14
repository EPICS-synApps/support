rem checkout.bat

echo off

rem Checkout the synApps trunk from the subversion repository

mkdir synAppsSVN
cd synAppsSVN

rem For file access
rem set APS_SVN=file:///home/joule/SVNSYNAP/svn

rem For https access
set APS_SVN=https://subversion.xray.aps.anl.gov/synApps
set GIT_SVN=https://github.com/epics-modules

svn co %APS_SVN%/support/trunk support
cd support

set aps_items=      
set git_items=

set aps_items=%aps_items% autosave
set aps_items=%aps_items% busy
set aps_items=%aps_items% calc
set git_items=%git_items% camac
set aps_items=%aps_items% caputRecorder
set aps_items=%aps_items% configure
set git_items=%git_items% dac128V   
set aps_items=%aps_items% delaygen
set aps_items=%aps_items% documentation
set git_items=%git_items% dxp
set aps_items=%aps_items% ebrick
set aps_items=%aps_items% ip
set git_items=%git_items% ip330
set git_items=%git_items% ipUnidig
set aps_items=%aps_items% love
set git_items=%git_items% mca
set git_items=%git_items% measComp
set git_items=%git_items% modbus
set aps_items=%aps_items% motor
set aps_items=%aps_items% optics
set git_items=%git_items% quadEM
set aps_items=%aps_items% sscan
set aps_items=%aps_items% softGlue
set aps_items=%aps_items% std
set aps_items=%aps_items% stream
set aps_items=%aps_items% utils
set aps_items=%aps_items% vac
set aps_items=%aps_items% vme
set aps_items=%aps_items% xxx

FOR %%i IN (%aps_items%) DO svn co %APS_SVN%/%%i/trunk %%i
FOR %%i IN (%git_items%) DO svn co %GIT_SVN%/%%i/trunk %%i
