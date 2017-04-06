#!/bin/bash

### clone all the synApps modules from GitHub

mkdir synAppsGIT
cd synAppsGIT

export GIT_BASE=https://github.com

### clone the main synApps/support
git clone ${GIT_BASE}/EPICS-synApps/support
cd support

GIT_DRIVERS=
GIT_ADMIN=

### define where each module is located now
GIT_DRIVERS+=" alive"
GIT_DRIVERS+=" asyn"
GIT_DRIVERS+=" autosave"
GIT_DRIVERS+=" busy"
GIT_DRIVERS+=" calc"
GIT_DRIVERS+=" camac"
GIT_DRIVERS+=" caputRecorder"
GIT_DRIVERS+=" dac128V"
GIT_DRIVERS+=" delaygen"
GIT_DRIVERS+=" dxp"
GIT_DRIVERS+=" ip"
GIT_DRIVERS+=" ip330"
GIT_DRIVERS+=" ipUnidig"
GIT_DRIVERS+=" love"
GIT_DRIVERS+=" mca"
GIT_DRIVERS+=" measComp"
GIT_DRIVERS+=" modbus"
GIT_DRIVERS+=" motor"
GIT_DRIVERS+=" optics"
GIT_DRIVERS+=" quadEM"
GIT_DRIVERS+=" softGlue"
GIT_DRIVERS+=" sscan"
GIT_DRIVERS+=" std"
GIT_DRIVERS+=" stream"
GIT_DRIVERS+=" vac"
GIT_DRIVERS+=" vme"
GIT_DRIVERS+=" xxx"
export GIT_DRIVERS

GIT_ADMIN+=" utils"
GIT_ADMIN+=" configure"
GIT_ADMIN+=" documentation"
export GIT_ADMIN

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
