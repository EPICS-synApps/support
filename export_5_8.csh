#!/bin/csh
setenv SVN https://subversion.xray.aps.anl.gov/synApps
mkdir synApps_5_8
cd synApps_5_8
svn export $SVN/support/tags/synApps_5_8 support
cd support
# modules
svn export $SVN/alive/tags/R1-0-0 alive-1-0
svn export $SVN/autosave/tags/R5-6-1 autosave-5-6-1
svn export $SVN/busy/tags/R1-6-1 busy-1-6-1
svn export $SVN/calc/tags/R3-4-2-1 calc-3-4-2-1
svn export $SVN/camac/tags/R2-7 camac-2-7
svn export $SVN/caputRecorder/tags/R1-4-2 caputRecorder-1-4-2
svn export $SVN/dac128V/tags/R2-8 dac128V-2-8
svn export $SVN/delaygen/tags/R1-1-1 delaygen-1-1-1
svn export $SVN/dxp/tags/R3-4 dxp-3-4
svn export $SVN/ip/tags/R2-17 ip-2-17
svn export $SVN/ip330/tags/R2-8 ip330-2-8
svn export $SVN/ipUnidig/tags/R2-10 ipUnidig-2-10
svn export $SVN/love/tags/R3-2-5 love-3-2-5
svn export $SVN/mca/tags/R7-6 mca-7-6
svn export $SVN/measComp/tags/R1-1 measComp-1-1
svn export $SVN/modbus/tags/R2-7 modbus-2-7
svn export $SVN/motor/tags/R6-9 motor-6-9
svn export $SVN/optics/tags/R2-9-3 optics-2-9-3
svn export $SVN/quadEM/tags/R5-0 quadEM-5-0
svn export $SVN/softGlue/tags/R2-4-3 softGlue-2-4-3
svn export $SVN/sscan/tags/R2-10-1 sscan-2-10-1
svn export $SVN/std/tags/R3-4 std-3-4
svn export $SVN/stream/tags/R2-6a stream-2-6a
svn export $SVN/vac/tags/R1-5-1 vac-1-5-1
svn export $SVN/vme/tags/R2-8-2 vme-2-8-2
svn export $SVN/xxx/tags/R5-8-3 xxx-5-8-3
# other directories
svn export $SVN/configure/tags/synApps_5_8 configure
svn export $SVN/utils/tags/synApps_5_8 utils
svn export $SVN/documentation/tags/synApps_5_8 documentation


# get areaDetector, ADCore, ADBinaries from https://github.com/areaDetector
wget https://github.com/areaDetector/areaDetector/archive/R2-0.tar.gz
tar zxf R2-0.tar.gz
rm R2-0.tar.gz

cd areaDetector-R2-0
wget https://github.com/areaDetector/ADCore/archive/R2-2.tar.gz
tar zxf R2-2.tar.gz
rm R2-2.tar.gz

wget https://github.com/areaDetector/ADBinaries/archive/R2-2.tar.gz
tar zxf R2-2.tar.gz
rm R2-2.tar.gz

cd ..

# get allenBradley-2-3
wget http://www.aps.anl.gov/epics/download/modules/allenBradley-2.3.tar.gz
tar xf allenBradley-2.3.tar.gz
mv allenBradley-2.3 allenBradley-2-3
rm allenBradley-2.3.tar.gz

svn export https://svn.aps.anl.gov/epics/asyn/tags/R4-26 asyn-4-26
svn export https://svn.aps.anl.gov/epics/ipac/tags/V2-13 ipac-2-13

# get seq-2-1-18 or seq-2-2-1 from http://www-csr.bessy.de/control/SoftDist/sequencer
setenv SEQ_URL http://www-csr.bessy.de/control/SoftDist/sequencer/releases/seq-2.2.1.tar.gz
wget http://www-csr.bessy.de/control/SoftDist/sequencer/releases/seq-2.2.1.tar.gz
tar zxf seq-2.2.1.tar.gz
mv seq-2.2.1 seq-2-2-1
rm seq-2.2.1.tar.gz

# get devIocStats-3-1-13 from http://www.slac.stanford.edu/grp/cd/soft/epics/site/devIocStats/
svn export https://svn.code.sf.net/p/epics/svn/applications/tags/iocStats/3-1-13 devIocStats-3-1-13
