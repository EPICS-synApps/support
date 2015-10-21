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
setenv APS_ITEMS "${APS_ITEMS} calc"
setenv APS_ITEMS "${APS_ITEMS} caputRecorder"
setenv APS_ITEMS "${APS_ITEMS} configure"
setenv APS_ITEMS "${APS_ITEMS} delaygen"
setenv APS_ITEMS "${APS_ITEMS} documentation"
setenv APS_ITEMS "${APS_ITEMS} ebrick"
setenv APS_ITEMS "${APS_ITEMS} ip"
setenv APS_ITEMS "${APS_ITEMS} love"
setenv APS_ITEMS "${APS_ITEMS} optics"
setenv APS_ITEMS "${APS_ITEMS} softGlue"
setenv APS_ITEMS "${APS_ITEMS} sscan"
setenv APS_ITEMS "${APS_ITEMS} std"
setenv APS_ITEMS "${APS_ITEMS} stream"
setenv APS_ITEMS "${APS_ITEMS} utils"
setenv APS_ITEMS "${APS_ITEMS} vac"
setenv APS_ITEMS "${APS_ITEMS} vme"
setenv APS_ITEMS "${APS_ITEMS} xxx"

setenv GIT_ITEMS "${GIT_ITEMS} autosave"
setenv GIT_ITEMS "${GIT_ITEMS} busy"
setenv GIT_ITEMS "${GIT_ITEMS} camac"
setenv GIT_ITEMS "${GIT_ITEMS} dac128V"
setenv GIT_ITEMS "${GIT_ITEMS} dxp"
setenv GIT_ITEMS "${GIT_ITEMS} ip330"
setenv GIT_ITEMS "${GIT_ITEMS} ipUnidig"
setenv GIT_ITEMS "${GIT_ITEMS} mca"
setenv GIT_ITEMS "${GIT_ITEMS} measComp"
setenv GIT_ITEMS "${GIT_ITEMS} modbus"
setenv GIT_ITEMS "${GIT_ITEMS} motor"
setenv GIT_ITEMS "${GIT_ITEMS} quadEM"


### checkout modules from the APS subversion repository
foreach i ( ${APS_ITEMS} )
    svn co ${APS_SVN}/$i/trunk $i
end

### checkout modules from GitHub using subversion
foreach i ( ${GIT_ITEMS} )
    svn co ${GIT_SVN}/$i/trunk $i
end
