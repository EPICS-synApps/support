#!/bin/csh

### clone all the synApps modules from GitHub

mkdir synAppsGIT
cd synAppsGIT

setenv GIT_BASE   https://github.com

### clone the main synApps/support
git clone ${GIT_BASE}/EPICS-synApps/support
cd support

setenv GIT_DRIVERS ""
setenv GIT_ADMIN ""

### define where each module is located now
setenv GIT_DRIVERS "${GIT_DRIVERS} alive"
setenv GIT_DRIVERS "${GIT_DRIVERS} asyn"
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
setenv GIT_DRIVERS "${GIT_DRIVERS} optics"
setenv GIT_DRIVERS "${GIT_DRIVERS} quadEM"
setenv GIT_DRIVERS "${GIT_DRIVERS} softGlue"
setenv GIT_DRIVERS "${GIT_DRIVERS} sscan"
setenv GIT_DRIVERS "${GIT_DRIVERS} std"
setenv GIT_DRIVERS "${GIT_DRIVERS} stream"
setenv GIT_DRIVERS "${GIT_DRIVERS} vac"
setenv GIT_DRIVERS "${GIT_DRIVERS} vme"
setenv GIT_DRIVERS "${GIT_DRIVERS} xxx"

setenv GIT_ADMIN "${GIT_ADMIN} utils"
setenv GIT_ADMIN "${GIT_ADMIN} configure"
setenv GIT_ADMIN "${GIT_ADMIN} documentation"

### clone driver modules from GitHub
foreach i ( ${GIT_ADMIN} )
    git clone ${GIT_BASE}/EPICS-synApps/$i.git
end

### clone driver modules from GitHub
foreach i ( ${GIT_DRIVERS} )
    git clone ${GIT_BASE}/epics-modules/$i.git
end

# EPICS areaDetector
git clone --recursive https://github.com/areaDetector/areaDetector.git
