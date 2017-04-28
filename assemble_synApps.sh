#!/bin/bash

# This file is intended to gather everything in or used in synApps.
# The version numbers in this file are not guaranteed to be up to date,
# and the modules are not guaranteed to work or even build together.

get_repo()
{
	PROJECT=$1
	MODULE_NAME=$2
	RELEASE_NAME=$3
	TAG=$4
	PREFIX=$5
	
	echo
	echo "Grabbing $MODULE_NAME at tag: $TAG"
	echo
	
	git clone git://github.com/$PROJECT/$MODULE_NAME.git $PREFIX$MODULE_NAME-${TAG/./-}  >> git_status.txt
	
	CURR=$(pwd)
	
	cd $PREFIX$MODULE_NAME-${TAG/./-}
	git checkout -q $TAG
	cd $CURR
	echo "$RELEASE_NAME=\$(SUPPORT)/$PREFIX$MODULE_NAME-${TAG/./-}" >> RELEASE_files.txt
	
	echo
}

get_support()
{
	git clone -q git://github.com/EPICS-synApps/$1.git
	cd $1
	git checkout -q $2
	cd ..
}



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

#get_repo   Git Project      Git Repo         RELEASE Name     Tag        Subdirectory
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
get_repo    areaDetector     areaDetector     AREADETECTOR     R2-4
get_repo    areaDetector     ADCore           ADCORE           R2-4      areaDetector-R2-4/
get_repo    areaDetector     ADBinaries       ADBINARIES       R2-2      areaDetector-R2-4/
get_repo    epics-modules    stream           STREAM           master

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
