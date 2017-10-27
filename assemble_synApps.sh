#!/bin/bash
shopt -s expand_aliases

EPICS_BASE=/APSshare/epics/base-3.15.5

SUPPORT=synApps_5_8
CONFIGURE=synApps_5_8
UTILS=synApps_5_8
DOCUMENTATION=synApps_5_8

ALLENBRADLEY=2.3
ALIVE=R1-0-1
AREA_DETECTOR=R2-6
ASYN=R4-31
AUTOSAVE=R5-7-1
BUSY=R1-6-1
CALC=R3-6-1
CAMAC=R2-7
CAPUTRECORDER=R1-6
DAC128V=R2-8
DELAYGEN=R1-1-1
DXP=R3-5
DEVIOCSTATS=3.1.14
IP=R2-10
IPAC=2.14
IP330=R2-8
IPUNIDIG=R2-10
LOVE=R3-2-5
MCA=R7-6
MEASCOMP=R1-3-1
MODBUS=R2-9
MOTOR=R6-9
OPTICS=R2-11
QUADEM=R7-0
SNCSEQ=2.2.4
SOFTGLUE=R2-8
SSCAN=R2-10-2
STD=R3-4-1
STREAM=R2-7-7
VAC=R1-5-1
VME=R2-8-2
XXX=R5-8




shallow_repo()
{
	PROJECT=$1
	MODULE_NAME=$2
	RELEASE_NAME=$3
	TAG=$4
	
	FOLDER_NAME=$MODULE_NAME-${TAG//./-}
	
	echo
	echo "Grabbing $MODULE_NAME at tag: $TAG"
	echo
	
	git clone -q --branch $TAG --depth 1 git://github.com/$PROJECT/$MODULE_NAME.git $FOLDER_NAME
	
	echo "$RELEASE_NAME=\$(SUPPORT)/$FOLDER_NAME" >> ./configure/RELEASE
	
	echo
}

full_repo()
{
	PROJECT=$1
	MODULE_NAME=$2
	RELEASE_NAME=$3
	TAG=$4
	
	FOLDER_NAME=$MODULE_NAME-${TAG//./-}
	
	echo
	echo "Grabbing $MODULE_NAME at tag: $TAG"
	echo
	
	git clone -q git://github.com/$PROJECT/$MODULE_NAME.git $FOLDER_NAME
	
	CURR=$(pwd)
	
	cd $FOLDER_NAME
	git checkout -q $TAG
	cd $CURR
	echo "$RELEASE_NAME=\$(SUPPORT)/$FOLDER_NAME" >> ./configure/RELEASE
	
	echo
}


shallow_support()
{
	git clone -q --branch $2 --depth 1 git://github.com/EPICS-synApps/$1.git
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

get_support support $SUPPORT
cd support

get_support configure      $CONFIGURE
get_support utils          $UTILS
get_support documentation  $DOCUMENTATION


echo "SUPPORT=$(pwd)" > configure/RELEASE
echo '-include $(TOP)/configure/SUPPORT.$(EPICS_HOST_ARCH)' >> configure/RELEASE
echo "EPICS_BASE=$EPICS_BASE" >> configure/RELEASE
echo '-include $(TOP)/configure/EPICS_BASE' >> configure/RELEASE
echo '-include $(TOP)/configure/EPICS_BASE.$(EPICS_HOST_ARCH)' >> configure/RELEASE
echo "" >> configure/RELEASE
echo "" >> configure/RELEASE

# modules ##################################################################

#                               get_repo Git Project    Git Repo       RELEASE Name   Tag
if [[ $ALIVE ]];         then   get_repo epics-modules  alive          ALIVE          $ALIVE         ; fi
if [[ $ASYN ]];          then   get_repo epics-modules  asyn           ASYN           $ASYN          ; fi
if [[ $AUTOSAVE ]];      then   get_repo epics-modules  autosave       AUTOSAVE       $AUTOSAVE      ; fi
if [[ $BUSY ]];          then   get_repo epics-modules  busy           BUSY           $BUSY          ; fi
if [[ $CALC ]];          then   get_repo epics-modules  calc           CALC           $CALC          ; fi
if [[ $CAMAC ]];         then   get_repo epics-modules  camac          CAMAC          $CAMAC         ; fi
if [[ $CAPUTRECORDER ]]; then   get_repo epics-modules  caputRecorder  CAPUTRECORDER  $CAPUTRECORDER ; fi
if [[ $DAC128V ]];       then   get_repo epics-modules  dac128V        DAC128V        $DAC128V       ; fi
if [[ $DELAYGEN ]];      then   get_repo epics-modules  delaygen       DELAYGEN       $DELAYGEN      ; fi
if [[ $DXP ]];           then   get_repo epics-modules  dxp            DXP            $DXP           ; fi
if [[ $DEVIOCSTATS ]];   then   get_repo epics-modules  iocStats       DEVIOCSTATS    $DEVIOCSTATS   ; fi
if [[ $IP ]];            then   get_repo epics-modules  ip             IP             $IP            ; fi
if [[ $IPAC ]];          then   get_repo epics-modules  ipac           IPAC           $IPAC          ; fi
if [[ $IP330 ]];         then   get_repo epics-modules  ip330          IP330          $IP330         ; fi
if [[ $IPUNIDIG ]];      then   get_repo epics-modules  ipUnidig       IPUNIDIG       $IPUNIDIG      ; fi
if [[ $LOVE ]];          then   get_repo epics-modules  love           LOVE           $LOVE          ; fi
if [[ $MCA ]];           then   get_repo epics-modules  mca            MCA            $MCA           ; fi
if [[ $MEASCOMP ]];      then   get_repo epics-modules  measComp       MEASCOMP       $MEASCOMP      ; fi
if [[ $MODBUS ]];        then   get_repo epics-modules  modbus         MODBUS         $MODBUS        ; fi
if [[ $MOTOR ]];         then   get_repo epics-modules  motor          MOTOR          $MOTOR         ; fi
if [[ $OPTICS ]];        then   get_repo epics-modules  optics         OPTICS         $OPTICS        ; fi
if [[ $QUADEM ]];        then   get_repo epics-modules  quadEM         QUADEM         $QUADEM        ; fi
if [[ $SOFTGLUE ]];      then   get_repo epics-modules  softGlue       SOFTGLUE       $SOFTGLUE      ; fi
if [[ $SSCAN ]];         then   get_repo epics-modules  sscan          SSCAN          $SSCAN         ; fi
if [[ $STD ]];           then   get_repo epics-modules  std            STD            $STD           ; fi
if [[ $VAC ]];           then   get_repo epics-modules  vac            VAC            $VAC           ; fi
if [[ $VME ]];           then   get_repo epics-modules  vme            VME            $VME           ; fi
if [[ $XXX ]];           then   get_repo epics-modules  xxx            XXX            $XXX           ; fi


if [[ $STREAM ]]
then

get_repo  epics-modules  stream  STREAM  $STREAM

cd stream-$STREAM
git submodule init
git submodule update
cd ..

fi


if [[ $AREA_DETECTOR ]]
then 

get_repo  areaDetector  areaDetector  AREA_DETECTOR  $AREA_DETECTOR

cd areaDetector-$AREA_DETECTOR
git submodule init
git submodule update ADCore
git submodule update ADSupport
git submodule update ADSimDetector
cd ..

echo 'ADCORE=$(AREA_DETECTOR)/ADCore' >> ./configure/RELEASE
echo 'ADSUPPORT=$(AREA_DETECTOR)/ADSupport' >> ./configure/RELEASE
echo 'ADSIMDETECTOR=$(AREA_DETECTOR)/ADSimDetector' >> ./configure/RELEASE

fi


if [[ $SNCSEQ ]]
then

# seq
wget http://www-csr.bessy.de/control/SoftDist/sequencer/releases/seq-$SNCSEQ.tar.gz
tar zxf seq-$SNCSEQ.tar.gz
# The synApps build can't handle '.'
mv seq-$SNCSEQ seq-${SNCSEQ//./-}
rm -f seq-$SNCSEQ.tar.gz
echo "SNCSEQ=\$(SUPPORT)/seq-${SNCSEQ//./-}" >> ./configure/RELEASE

fi

if [[ $ALLENBRADLEY ]]
then

# get allenBradley-2-3
wget http://www.aps.anl.gov/epics/download/modules/allenBradley-$ALLENBRADLEY.tar.gz
tar xf allenBradley-$ALLENBRADLEY.tar.gz
mv allenBradley-$ALLENBRADLEY allenBradley-${ALLENBRADLEY//./-}
rm -f allenBradley-$ALLENBRADLEY.tar.gz
echo "ALLENBRADLEY=\$(SUPPORT)/allenBradley-${ALLENBRADLEY//./-}" >> ./configure/RELEASE

fi


if [[ $ETHERIP ]]
then

# etherIP
wget https://github.com/EPICSTools/ether_ip/archive/ether_ip-2-26.tar.gz
tar zxf ether_ip-2-26.tar.gz
mv ether_ip-ether_ip-2-26 ether_ip-2-26
rm -f ether_ip-2-26.tar.gz
echo 'ETHERIP=$(SUPPORT)/ether_ip-2-26' >> ./configure/RELEASE


fi


make release
