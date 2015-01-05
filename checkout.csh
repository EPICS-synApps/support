#!/bin/csh
mkdir synAppsSVN
cd synAppsSVN

# For file access
#setenv SVN file:///home/joule/SVNSYNAP/svn

# For https access
setenv SVN https://subversion.xray.aps.anl.gov/synApps

svn co $SVN/support/trunk support
cd support
foreach i ( alive autosave busy calc camac caputRecorder configure dac128V delaygen documentation dxp ebrick ip ip330 ipUnidig love mca measComp modbus motor optics quadEM sscan softGlue std stream utils vac vme xxx )
	svn co $SVN/$i/trunk $i
end
