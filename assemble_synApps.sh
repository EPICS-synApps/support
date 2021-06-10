#!/bin/bash
shopt -s expand_aliases

# Command-line arguments
args=$*
# Flags set by command-line arguments
FULL_CLONE=False
CONFIG_SOURCED=False

# Handle command-line arguments
for arg in ${args}
do
  if [ ${arg} == "full" ]
  then
    FULL_CLONE=True
  else
    if [ -e ${arg} ]
    then
      echo "Sourcing ${arg}"
      source ${arg}
      CONFIG_SOURCED=True
    else
      echo "${arg} does not exist."
    fi
  fi
done

echo "FULL_CLONE = ${FULL_CLONE}"

if [ ${CONFIG_SOURCED} == "False" ]
then
echo "Using default configuration"

EPICS_BASE=/APSshare/epics/base-7.0.4.1

HAVE_HIDAPI=NO
WITH_PVA=YES

# The name of the synApps directory can be customized
#!SYNAPPS_DIR=synApps_X_X

SUPPORT=master

ALLENBRADLEY=2.3
ALIVE=R1-3-1
AREA_DETECTOR=R3-11
ASYN=R4-42
AUTOSAVE=R5-10-2
BUSY=R1-7-3
CALC=R3-7-4
CAMAC=R2-7-3
CAPUTRECORDER=R1-7-3
DAC128V=R2-10-1
DELAYGEN=R1-2-2
DXP=R6-0
DXPSITORO=R1-2
DEVIOCSTATS=3.1.16
ETHERIP=ether_ip-3-2
GALIL=V3-6
IP=R2-21
IPAC=2.16
IP330=R2-10
IPUNIDIG=R2-12
LOVE=R3-2-8
LUA=R3-0-2
MCA=R7-9
MEASCOMP=R2-5-1
MODBUS=R3-2
MOTOR=R7-2-2
OPTICS=R2-13-5
QUADEM=R9-4
SNCSEQ=2.2.9
SOFTGLUE=R2-8-3
SOFTGLUEZYNQ=R2-0-3
SSCAN=R2-11-4
SCALER=4.0
STD=R3-6-2
STREAM=2.8.16
VAC=R1-9-1
VME=R2-9-3
YOKOGAWA_DAS=R2-0-1
XSPRESS3=2-5
XXX=master
fi


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
	
	git clone -q --branch $TAG --depth 1 https://github.com/$PROJECT/$MODULE_NAME.git $FOLDER_NAME
	
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
	
	git clone -q https://github.com/$PROJECT/$MODULE_NAME.git $FOLDER_NAME
	
	CURR=$(pwd)
	
	cd $FOLDER_NAME
	git checkout -q $TAG
	cd "$CURR"
	echo "$RELEASE_NAME=\$(SUPPORT)/$FOLDER_NAME" >> ./configure/RELEASE
	
	echo
}


shallow_support()
{
	git clone -q --branch $2 --depth 1 https://github.com/EPICS-synApps/$1.git
}


full_support()
{
	git clone -q https://github.com/EPICS-synApps/$1.git
	cd $1
	git checkout -q $2
	cd ..
}


if [ ${FULL_CLONE} == "True" ]
then
	alias get_support='full_support'
	alias get_repo='full_repo'
else
	# A shallow clone is the default
	alias get_support='shallow_support'
	alias get_repo='shallow_repo'
fi

if [ -z "${SYNAPPS_DIR}" ]
then
SYNAPPS_DIR=synApps
fi


# Assume user has nothing but this file, just in case that's true.
mkdir ${SYNAPPS_DIR}
cd ${SYNAPPS_DIR}

get_support support $SUPPORT
cd support

SUPPORT=$(pwd)

echo "SUPPORT=$SUPPORT" > configure/RELEASE
echo '-include $(TOP)/configure/SUPPORT.$(EPICS_HOST_ARCH)' >> configure/RELEASE
echo "EPICS_BASE=$EPICS_BASE" >> configure/RELEASE
echo '-include $(TOP)/configure/EPICS_BASE' >> configure/RELEASE
echo '-include $(TOP)/configure/EPICS_BASE.$(EPICS_HOST_ARCH)' >> configure/RELEASE
echo "" >> configure/RELEASE
echo "" >> configure/RELEASE

# modules ##################################################################

#                               get_repo Git Project            Git Repo       RELEASE Name   Tag
if [[ $ALIVE ]];         then   get_repo epics-modules          alive          ALIVE          $ALIVE         ; fi
if [[ $ASYN ]];          then   get_repo epics-modules          asyn           ASYN           $ASYN          ; fi
if [[ $AUTOSAVE ]];      then   get_repo epics-modules          autosave       AUTOSAVE       $AUTOSAVE      ; fi
if [[ $BUSY ]];          then   get_repo epics-modules          busy           BUSY           $BUSY          ; fi
if [[ $CALC ]];          then   get_repo epics-modules          calc           CALC           $CALC          ; fi
if [[ $CAMAC ]];         then   get_repo epics-modules          camac          CAMAC          $CAMAC         ; fi
if [[ $CAPUTRECORDER ]]; then   get_repo epics-modules          caputRecorder  CAPUTRECORDER  $CAPUTRECORDER ; fi
if [[ $DAC128V ]];       then   get_repo epics-modules          dac128V        DAC128V        $DAC128V       ; fi
if [[ $DELAYGEN ]];      then   get_repo epics-modules          delaygen       DELAYGEN       $DELAYGEN      ; fi
if [[ $DXP ]];           then   get_repo epics-modules          dxp            DXP            $DXP           ; fi
if [[ $DXPSITORO ]];     then   get_repo epics-modules          dxpSITORO      DXPSITORO      $DXPSITORO     ; fi
if [[ $DEVIOCSTATS ]];   then   get_repo epics-modules          iocStats       DEVIOCSTATS    $DEVIOCSTATS   ; fi
if [[ $ETHERIP ]];       then   get_repo EPICSTools             ether_ip       ETHERIP        $ETHERIP       ; fi
if [[ $GALIL ]];         then   get_repo motorapp               Galil-3-0      GALIL          $GALIL         ; fi
if [[ $IP ]];            then   get_repo epics-modules          ip             IP             $IP            ; fi
if [[ $IPAC ]];          then   get_repo epics-modules          ipac           IPAC           $IPAC          ; fi
if [[ $IP330 ]];         then   get_repo epics-modules          ip330          IP330          $IP330         ; fi
if [[ $IPUNIDIG ]];      then   get_repo epics-modules          ipUnidig       IPUNIDIG       $IPUNIDIG      ; fi
if [[ $LOVE ]];          then   get_repo epics-modules          love           LOVE           $LOVE          ; fi
if [[ $LUA ]];           then   get_repo epics-modules          lua            LUA            $LUA           ; fi
if [[ $MCA ]];           then   get_repo epics-modules          mca            MCA            $MCA           ; fi
if [[ $MEASCOMP ]];      then   get_repo epics-modules          measComp       MEASCOMP       $MEASCOMP      ; fi
if [[ $MODBUS ]];        then   get_repo epics-modules          modbus         MODBUS         $MODBUS        ; fi
if [[ $MOTOR ]];         then   get_repo epics-modules          motor          MOTOR          $MOTOR         ; fi
if [[ $OPTICS ]];        then   get_repo epics-modules          optics         OPTICS         $OPTICS        ; fi
if [[ $QUADEM ]];        then   get_repo epics-modules          quadEM         QUADEM         $QUADEM        ; fi
if [[ $SCALER ]];        then   get_repo epics-modules          scaler         SCALER         $SCALER        ; fi
if [[ $SOFTGLUE ]];      then   get_repo epics-modules          softGlue       SOFTGLUE       $SOFTGLUE      ; fi
if [[ $SOFTGLUEZYNQ ]];  then   get_repo epics-modules          softGlueZynq   SOFTGLUEZYNQ   $SOFTGLUEZYNQ  ; fi
if [[ $SSCAN ]];         then   get_repo epics-modules          sscan          SSCAN          $SSCAN         ; fi
if [[ $STD ]];           then   get_repo epics-modules          std            STD            $STD           ; fi
if [[ $STREAM ]];        then   get_repo paulscherrerinstitute  StreamDevice   STREAM         $STREAM        ; fi
if [[ $VAC ]];           then   get_repo epics-modules          vac            VAC            $VAC           ; fi
if [[ $VME ]];           then   get_repo epics-modules          vme            VME            $VME           ; fi
if [[ $XSPRESS3 ]];      then   get_repo epics-modules          xspress3       XSPRESS3       $XSPRESS3      ; fi
if [[ $YOKOGAWA_DAS ]];  then   get_repo epics-modules          Yokogawa_DAS   YOKOGAWA_DAS   $YOKOGAWA_DAS  ; fi
if [[ $XXX ]];           then   get_repo epics-modules          xxx            XXX            $XXX           ; fi


if [[ $AREA_DETECTOR ]]
then 

get_repo  areaDetector  areaDetector  AREA_DETECTOR  $AREA_DETECTOR

echo "ADCORE=\$(AREA_DETECTOR)/ADCore" >> configure/RELEASE
echo "ADSUPPORT=\$(AREA_DETECTOR)/ADSupport" >> configure/RELEASE

cd areaDetector-$AREA_DETECTOR
git submodule init
git submodule update ADCore
git submodule update ADSupport
git submodule update ADSimDetector

cd ADCore/iocBoot

cp EXAMPLE_commonPlugins.cmd commonPlugins.cmd
cp EXAMPLE_commonPlugin_settings.req commonPlugin_settings.req

cd ../..

cd configure
cp EXAMPLE_CONFIG_SITE.local       CONFIG_SITE.local
cp EXAMPLE_CONFIG_SITE.local.WIN32 CONFIG_SITE.local.WIN32
# make release will give the correct paths for these files, so we just need to rename them
cp EXAMPLE_RELEASE_PRODS.local     RELEASE_PRODS.local
cp EXAMPLE_RELEASE_LIBS.local      RELEASE_LIBS.local
cp EXAMPLE_RELEASE.local           RELEASE.local

# vxWorks has pthread and other issues
echo 'WITH_GRAPHICSMAGICK = NO' >> CONFIG_SITE.local.vxWorks
echo 'WITH_BLOSC = NO' >> CONFIG_SITE.local.vxWorks
echo 'WITH_BITSHUFFLE = NO' >> CONFIG_SITE.local.vxWorks


# linux-arm has X11 and other issues
echo 'WITH_BITSHUFFLE = NO' >> CONFIG_SITE.local.linux-x86_64.linux-arm
echo 'WITH_GRAPHICSMAGICK = NO' >> CONFIG_SITE.local.linux-x86_64.linux-arm
echo 'WITH_BITSHUFFLE = NO' >> CONFIG_SITE.local.linux-x86.linux-arm
echo 'WITH_GRAPHICSMAGICK = NO' >> CONFIG_SITE.local.linux-x86.linux-arm

if [ $(WITH_PVA) == "YES" ]
then
	sed -i s:'WITH_PVA  = YES':'WITH_PVA = NO':g CONFIG_SITE.local
	sed -i s:'WITH_QSRV = YES':'WITH_QSRV = NO':g CONFIG_SITE.local
fi

# Enable building ADSimDetector
sed -i s:'#ADSIMDETECTOR':'ADSIMDETECTOR':g RELEASE.local

cd ../..

fi

if [[ $DXP ]]
then
	cd dxp-$DXP
	echo "LINUX_USB_INSTALLED = NO" >> ./configure/CONFIG_SITE.linux-x86_64.linux-arm
	echo "LINUX_USB_INSTALLED = NO" >> ./configure/CONFIG_SITE.linux-x86.linux-arm
	cd ..
fi

if [[ $ETHERIP ]]
then
	cd ether_ip-$ETHERIP
	echo "EPICS_BASE=" >> ./configure/RELEASE
	cd ..
fi

if [[ $IPAC ]]
then
	cd ipac-${IPAC//./-}
	echo "-include \$(TOP)/../RELEASE.local" >> ./configure/RELEASE
	echo "-include \$(TOP)/../RELEASE.\$(EPICS_HOST_ARCH).local" >> ./configure/RELEASE
	echo "-include \$(TOP)/configure/RELEASE.local" >> ./configure/RELEASE
	sed -i s:'#registrar(vipc310Registrar)':'registrar(vipc310Registrar)':g drvIpac/drvIpac.dbd
	sed -i s:'#registrar(vipc610Registrar)':'registrar(vipc610Registrar)':g drvIpac/drvIpac.dbd
	sed -i s:'#registrar(vipc616Registrar)':'registrar(vipc616Registrar)':g drvIpac/drvIpac.dbd
	sed -i s:'#registrar(tvme200Registrar)':'registrar(tvme200Registrar)':g drvIpac/drvIpac.dbd
	sed -i s:'#registrar(xy9660Registrar)':'registrar(xy9660Registrar)':g drvIpac/drvIpac.dbd

	cd ..
fi

if [[ $MCA ]]
then
	cd mca-$MCA
	echo "LINUX_LIBUSB-1.0_INSTALLED = NO" >> ./configure/CONFIG_SITE.linux-x86_64.linux-arm
	echo "LINUX_LIBUSB-1.0_INSTALLED = NO" >> ./configure/CONFIG_SITE.linux-x86.linux-arm
	cd ..
fi

if [[ $MEASCOMP ]]
then
	if [ ${HAVE_HIDAPI} == "NO" ]
	then
		cd measComp-$MEASCOMP
		cd configure
		sed -i 's/HAVE_HIDAPI=YES/HAVE_HIDAPI=NO/g' ./CONFIG_SITE*
		cd ../..
	fi
fi

if [[ $MOTOR ]]
then
	cd motor-$MOTOR
	
	git submodule init
	git submodule update
	
	cd ..
fi

if [[ $STREAM ]]
then
	cd StreamDevice-${STREAM//./-}
	
	# Use the EPICS makefile, rather than PSI's
	rm GNUmakefile
	
	# Don't install to synApps/support
	sed -i 's/TOP = ../TOP = ./g' ./Makefile
	sed -i 's/TOP = ..\/../TOP = ../g' ./streamApp/Makefile
	sed -i 's/TOP = ..\/../TOP = ../g' ./src/Makefile
	
	# Comment out PCRE
	sed -i 's/PCRE=/#PCRE=/g' ./configure/RELEASE
	
	echo "SSCAN=" >> ./configure/RELEASE
	echo "STREAM=" >> ./configure/RELEASE
  echo "-include \$(TOP)/../RELEASE.local" >> ./configure/RELEASE
  echo "-include \$(TOP)/../RELEASE.\$(EPICS_HOST_ARCH).local" >> ./configure/RELEASE
  echo "-include \$(TOP)/configure/RELEASE.local" >> ./configure/RELEASE
	sed -i 's/#PROD_LIBS += sscan/PROD_LIBS += sscan/g' ./streamApp/Makefile
	cd ..
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

if [[ $CALC ]]
then

# Uncomment sseq support in calc
cd calc-$CALC
sed -i s:'#SNCSEQ':'SNCSEQ':g configure/RELEASE
cd ..

fi

fi


if [[ $ALLENBRADLEY ]]
then

# get allenBradley-2-3
wget http://www.aps.anl.gov/epics/download/modules/allenBradley-$ALLENBRADLEY.tar.gz
tar xf allenBradley-$ALLENBRADLEY.tar.gz
mv allenBradley-$ALLENBRADLEY allenBradley-${ALLENBRADLEY//./-}
rm -f allenBradley-$ALLENBRADLEY.tar.gz
ALLENBRADLEY=${ALLENBRADLEY//./-}
echo "ALLEN_BRADLEY=\$(SUPPORT)/allenBradley-${ALLENBRADLEY}" >> ./configure/RELEASE
cd allenBradley-$ALLENBRADLEY
echo "-include \$(TOP)/../RELEASE.local" >> ./configure/RELEASE
echo "-include \$(TOP)/../RELEASE.\$(EPICS_HOST_ARCH).local" >> ./configure/RELEASE
echo "-include \$(TOP)/configure/RELEASE.local" >> ./configure/RELEASE
cd ..

fi

if [[ $GALIL ]]
then

cd Galil-3-0-$GALIL
cp -r ${GALIL//V}/. ./
rm -rf ${GALIL//V}

cp ./config/GALILRELEASE ./configure/RELEASE.local

sed -i s:'#CROSS_COMPILER_TARGET_ARCHS.*':'CROSS_COMPILER_TARGET_ARCHS = ':g configure/CONFIG_SITE

cd ..

fi

make release
