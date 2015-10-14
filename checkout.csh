#!/bin/csh

### checkout the subversion development trunk for all the synApps modules

mkdir synAppsSVN
cd synAppsSVN

# For file access
#setenv APS_SVN file:///home/joule/SVNSYNAP/svn

### For https access
setenv APS_SVN    https://subversion.xray.aps.anl.gov/synApps
setenv GIT_SVN    https://github.com/epics-modules

### checkout the main synApps/support
svn co ${APS_SVN}/support/trunk support
cd support

setenv APS_ITEMS ""
setenv GIT_ITEMS ""

### define where each module is located now
setenv APS_ITEMS "${APS_ITEMS} alive"
setenv APS_ITEMS "${APS_ITEMS} autosave"
setenv APS_ITEMS "${APS_ITEMS} busy"
setenv APS_ITEMS "${APS_ITEMS} calc"
setenv GIT_ITEMS "${GIT_ITEMS} camac"
setenv APS_ITEMS "${APS_ITEMS} caputRecorder"
setenv APS_ITEMS "${APS_ITEMS} configure"
setenv GIT_ITEMS "${GIT_ITEMS} dac128V"
setenv APS_ITEMS "${APS_ITEMS} delaygen"
setenv APS_ITEMS "${APS_ITEMS} documentation"
setenv GIT_ITEMS "${GIT_ITEMS} dxp"
setenv APS_ITEMS "${APS_ITEMS} ebrick"
setenv APS_ITEMS "${APS_ITEMS} ip"
setenv GIT_ITEMS "${GIT_ITEMS} ip330"
setenv GIT_ITEMS "${GIT_ITEMS} ipUnidig"
setenv APS_ITEMS "${APS_ITEMS} love"
setenv GIT_ITEMS "${GIT_ITEMS} mca"
setenv GIT_ITEMS "${GIT_ITEMS} measComp"
setenv GIT_ITEMS "${GIT_ITEMS} modbus"
setenv APS_ITEMS "${APS_ITEMS} motor"
setenv APS_ITEMS "${APS_ITEMS} optics"
setenv GIT_ITEMS "${GIT_ITEMS} quadEM"
setenv APS_ITEMS "${APS_ITEMS} sscan"
setenv APS_ITEMS "${APS_ITEMS} softGlue"
setenv APS_ITEMS "${APS_ITEMS} std"
setenv APS_ITEMS "${APS_ITEMS} stream"
setenv APS_ITEMS "${APS_ITEMS} utils"
setenv APS_ITEMS "${APS_ITEMS} vac"
setenv APS_ITEMS "${APS_ITEMS} vme"
setenv APS_ITEMS "${APS_ITEMS} xxx"

### checkout modules from the APS subversion repository
foreach i ( ${APS_ITEMS} )
    svn co ${APS_SVN}/$i/trunk $i
end

### checkout modules from GitHub using subversion
foreach i ( ${GIT_ITEMS} )
    svn co ${GIT_SVN}/$i/trunk $i
end
