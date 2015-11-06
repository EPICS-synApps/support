#!/bin/csh

### checkout the subversion development trunk for all the synApps modules

mkdir synAppsSVN
cd synAppsSVN

# For file access
#setenv APS_SVN file:///home/joule/SVNSYNAP/svn

### For https access
setenv APS_SVN    https://subversion.xray.aps.anl.gov/synApps
setenv GIT_BASE   https://github.com

### checkout the main synApps/support
svn co ${APS_SVN}/support/trunk support
cd support

setenv APS_ITEMS ""
setenv GIT_DRIVERS ""
setenv GIT_ADMIN ""

### define where each module is located now
setenv APS_ITEMS "${APS_ITEMS} ebrick"
setenv APS_ITEMS "${APS_ITEMS} optics"
setenv APS_ITEMS "${APS_ITEMS} softGlue"
setenv APS_ITEMS "${APS_ITEMS} sscan"
setenv APS_ITEMS "${APS_ITEMS} stream"
setenv APS_ITEMS "${APS_ITEMS} xxx"

setenv GIT_DRIVERS "${GIT_DRIVERS} alive"
setenv GIT_DRIVERS "${GIT_DRIVERS} autosave"
setenv GIT_DRIVERS "${GIT_DRIVERS} busy"
setenv GIT_DRIVERS "${GIT_DRIVERS} calc"
setenv GIT_DRIVERS "${GIT_DRIVERS} camac"
setenv GIT_DRIVERS "${GIT_DRIVERS} caputRecorder"
setenv GIT_DRIVERS "${GIT_DRIVERS} dac128V"
setenv GIT_DRIVERS "${GIT_DRIVERS} delaygen"
setenv GIT_DRIVERS "${GIT_DRIVERS} dxp"
setenv GIT_DRIVERS "${GIT_DRIVERS} ip"
setenv GIT_DRIVERS "${GIT_DRIVERS} ip330"
setenv GIT_DRIVERS "${GIT_DRIVERS} ipUnidig"
setenv GIT_DRIVERS "${GIT_DRIVERS} love"
setenv GIT_DRIVERS "${GIT_DRIVERS} mca"
setenv GIT_DRIVERS "${GIT_DRIVERS} measComp"
setenv GIT_DRIVERS "${GIT_DRIVERS} modbus"
setenv GIT_DRIVERS "${GIT_DRIVERS} motor"
setenv GIT_DRIVERS "${GIT_DRIVERS} quadEM"
setenv GIT_DRIVERS "${GIT_DRIVERS} std"
setenv GIT_DRIVERS "${GIT_DRIVERS} vac"
setenv GIT_DRIVERS "${GIT_DRIVERS} vme"

setenv GIT_ADMIN "${GIT_ADMIN} utils"
setenv GIT_ADMIN "${GIT_ADMIN} configure"
setenv GIT_ADMIN "${GIT_ADMIN} documentation"

### checkout driver modules from GitHub using subversion
foreach i ( ${GIT_ADMIN} )
    svn co ${GIT_BASE}/EPICS-synApps/$i/trunk $i
end

### checkout driver modules from GitHub using subversion
foreach i ( ${GIT_DRIVERS} )
    svn co ${GIT_BASE}/epics-modules/$i/trunk $i
end

### checkout modules from the APS subversion repository
foreach i ( ${APS_ITEMS} )
    svn co ${APS_SVN}/$i/trunk $i
end
