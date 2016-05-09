#!/bin/sh

### clone all the synApps modules from GitHub

mkdir synAppsGIT
cd synAppsGIT

export GIT_BASE=https://github.com

### clone the main synApps/support
git clone ${GIT_BASE}/EPICS-synApps/support
cd support

export GIT_DRIVERS=
export GIT_ADMIN=

### define where each module is located now
export GIT_DRIVERS+=" alive"
export GIT_DRIVERS+=" asyn"
export GIT_DRIVERS+=" autosave"
export GIT_DRIVERS+=" busy"
export GIT_DRIVERS+=" calc"
export GIT_DRIVERS+=" camac"
export GIT_DRIVERS+=" caputRecorder"
export GIT_DRIVERS+=" dac128V"
export GIT_DRIVERS+=" delaygen"
export GIT_DRIVERS+=" dxp"
export GIT_DRIVERS+=" ip"
export GIT_DRIVERS+=" ip330"
export GIT_DRIVERS+=" ipUnidig"
export GIT_DRIVERS+=" love"
export GIT_DRIVERS+=" mca"
export GIT_DRIVERS+=" measComp"
export GIT_DRIVERS+=" modbus"
export GIT_DRIVERS+=" motor"
export GIT_DRIVERS+=" optics"
export GIT_DRIVERS+=" quadEM"
export GIT_DRIVERS+=" softGlue"
export GIT_DRIVERS+=" sscan"
export GIT_DRIVERS+=" std"
export GIT_DRIVERS+=" stream"
export GIT_DRIVERS+=" vac"
export GIT_DRIVERS+=" vme"
export GIT_DRIVERS+=" xxx"

export GIT_ADMIN+=" utils"
export GIT_ADMIN+=" configure"
export GIT_ADMIN+=" documentation"

### clone driver modules from GitHub
for i in ${GIT_ADMIN}; do
    git clone ${GIT_BASE}/EPICS-synApps/${i}.git
done

### clone driver modules from GitHub
for i in ${GIT_DRIVERS}; do
    git clone ${GIT_BASE}/epics-modules/${i}.git
done

# EPICS areaDetector
git clone --recursive https://github.com/areaDetector/areaDetector.git
