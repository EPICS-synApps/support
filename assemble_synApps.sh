#!/bin/bash
shopt -s expand_aliases

# This file is intended to gather everything in or used in synApps.
# The version numbers in this file are not guaranteed to be up to date,
# and the modules are not guaranteed to work or even build together.

shallow_repo()
{
	PROJECT=$1
	MODULE_NAME=$2
	RELEASE_NAME=$3
	TAG=$4
	
	echo
	echo "Grabbing $MODULE_NAME at tag: $TAG"
	echo
	
	git clone --branch $TAG --depth 1 git://github.com/$PROJECT/$MODULE_NAME.git $MODULE_NAME-${TAG/./-}  >> git_status.txt
	
	echo "$RELEASE_NAME=\$(SUPPORT)/$MODULE_NAME-${TAG/./-}" >> RELEASE_files.txt
	
	echo
}

full_repo()
{
	PROJECT=$1
	MODULE_NAME=$2
	RELEASE_NAME=$3
	TAG=$4
	
	echo
	echo "Grabbing $MODULE_NAME at tag: $TAG"
	echo
	
	git clone git://github.com/$PROJECT/$MODULE_NAME.git $MODULE_NAME-${TAG/./-}  >> git_status.txt
	
	CURR=$(pwd)
	
	cd $MODULE_NAME-${TAG/./-}
	git checkout -q $TAG
	cd $CURR
	echo "$RELEASE_NAME=\$(SUPPORT)/$MODULE_NAME-${TAG/./-}" >> RELEASE_files.txt
	
	echo
}


shallow_support()
{
	git clone --branch $2 --depth 1 git://github.com/EPICS-synApps/$1.git
}


full_support()
{
	git clone -q git://github.com/EPICS-synApps/$1.git
	cd $1
	git checkout -q $2
	cd ..
}

alias get_support='shallow_support'
alias get_repo='shallow_repo'

if [ "$1" == "full" ]; then
	alias get_support='full_support'
	alias get_repo='full_repo'
fi


# Assume user has nothing but this file, just in case that's true.
mkdir synApps
cd synApps

get_support support synApps_5_8
cd support

get_support configure        synApps_5_8
get_support utils            synApps_5_8
get_support documentation    synApps_5_8

echo '#Edit configure/RELEASE with the content of this file' >RELEASE_files.txt

# modules ##################################################################

#get_repo   Git Project      Git Repo         RELEASE Name     Tag
get_repo    epics-modules    alive            ALIVE            R1-0-1
get_repo    epics-modules    asyn             ASYN             R4-31
get_repo    epics-modules    autosave         AUTOSAVE         R5-7-1
get_repo    epics-modules    busy             BUSY             R1-6-1
get_repo    epics-modules    calc             CALC             R3-6-1
get_repo    epics-modules    camac            CAMAC            R2-7
get_repo    epics-modules    caputRecorder    CAPUTRECORDER    R1-6
get_repo    epics-modules    dac128V          DAC128V          R2-8
get_repo    epics-modules    delaygen         DELAYGEN         R1-1-1
get_repo    epics-modules    dxp              DXP              R3-5
get_repo    epics-modules    iocStats         DEVIOCSTATS      3.1.14
get_repo    epics-modules    ip               IP               R2-10
get_repo    epics-modules    ipac             IPAC             2.14
get_repo    epics-modules    ip330            IP330            R2-8
get_repo    epics-modules    ipUnidig         IPUNIDIG         R2-10
get_repo    epics-modules    love             LOVE             R3-2-5
get_repo    epics-modules    mca              MCA              R7-6
get_repo    epics-modules    measComp         MEASCOMP         R1-3-1
get_repo    epics-modules    modbus           MODBUS           R2-9
get_repo    epics-modules    motor            MOTOR            R6-9
get_repo    epics-modules    optics           OPTICS           R2-11
get_repo    epics-modules    quadEM           QUADEM           R7-0
get_repo    epics-modules    softGlue         SOFTGLUE         R2-8
get_repo    epics-modules    sscan            SSCAN            R2-10-2
get_repo    epics-modules    std              STD              R3-4-1
get_repo    epics-modules    vac              VAC              R1-5-1
get_repo    epics-modules    vme              VME              R2-8-2
get_repo    epics-modules    xxx              XXX              R5-8
get_repo    epics-modules    stream           STREAM           R2-7-7
get_repo    areaDetector     areaDetector     AREA_DETECTOR    R2-6

cd areaDetector-R2-6
git submodule init
git submodule update ADCore
git submodule update ADSupport
git submodule update ADSimDetector
cd ..

echo 'ADCORE=$(AREA_DETECTOR)/ADCore' >> RELEASE_files.txt
echo 'ADSUPPORT=$(AREA_DETECTOR)/ADSupport' >> RELEASE_files.txt
echo 'ADSIMDETECTOR=$(AREA_DETECTOR)/ADSimDetector' >> RELEASE_files.txt

cd stream-master
git submodule init
git submodule update
cd ..


# get allenBradley-2-3
wget http://www.aps.anl.gov/epics/download/modules/allenBradley-2.3.tar.gz
tar xf allenBradley-2.3.tar.gz
mv allenBradley-2.3 allenBradley-2-3
rm -f allenBradley-2.3.tar.gz
echo 'ALLENBRADLEY=$(SUPPORT)/allenBradley-2-3' >>RELEASE_files.txt

# seq
wget http://www-csr.bessy.de/control/SoftDist/sequencer/releases/seq-2.2.4.tar.gz
tar zxf seq-2.2.4.tar.gz
# The synApps build can't handle '.'
mv seq-2.2.4 seq-2-2-4
rm -f seq-2.2.4.tar.gz
echo 'SNCSEQ=$(SUPPORT)/seq-2-2-4' >>RELEASE_files.txt

# etherIP
#wget https://github.com/EPICSTools/ether_ip/archive/ether_ip-2-26.tar.gz
#tar zxf ether_ip-2-26.tar.gz
#mv ether_ip-ether_ip-2-26 ether_ip-2-26
#rm -f ether_ip-2-26.tar.gz
#echo 'ETHERIP=$(SUPPORT)/ether_ip-2-26' >>RELEASE_files.txt

echo "See RELEASE_files.txt"
