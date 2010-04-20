#!/bin/csh
mkdir synAppsSVN
cd synAppsSVN

# For file access
#setenv SVN file:///home/joule/SVNSYNAP/svn

# For https access
setenv SVN https://subversion.xor.aps.anl.gov/synApps

svn co $SVN/support/trunk support
cd support
foreach i ( areaDetector autosave busy calc camac camac_use configure dac128V delaygen documentation dxp ebrick ip ip330 ipUnidig ip_use love mca modbus motor optics quadEM sscan softGlue std stream vac vme vxStats xxx )
	svn co $SVN/$i/trunk $i
end
svn co $SVN/support/utils/trunk utils

