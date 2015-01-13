rem checkout.bat

echo off

rem Checkout the synApps trunk from the subversion repository

mkdir synAppsSVN
cd synAppsSVN

rem For file access
rem set SVN=file:///home/joule/SVNSYNAP/svn

rem For https access
set SVN=https://subversion.xray.aps.anl.gov/synApps

svn co %SVN%/support/trunk support
cd support

set items= autosave busy calc camac caputRecorder configure
set items=%items% dac128V delaygen documentation dxp ebrick
set items=%items% ip ip330 ipUnidig love mca measComp modbus motor
set items=%items% optics quadEM sscan softGlue std stream
set items=%items% utils vac vme xxx

FOR %%i IN (%items%) DO svn co %SVN%/%%i/trunk %%i
