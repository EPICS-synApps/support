#!/bin/csh
setenv SVN https://subversion.xor.aps.anl.gov/synApps
mkdir synApps_5_6
cd synApps_5_6
svn export $SVN/support/tags/synApps_5_6 support
cd support
# modules
svn export $SVN/areaDetector/tags/R1-7-1 areaDetector-1-7-1
svn export $SVN/autosave/tags/R4-8 autosave-4-8
svn export $SVN/busy/tags/R1-4 busy-1-4
svn export $SVN/calc/tags/R2-9 calc-2-9
svn export $SVN/camac/tags/R2-7 camac-2-7
svn export $SVN/dac128V/tags/R2-7 dac128V-2-7
svn export $SVN/delaygen/tags/R1-0-7 delaygen-1-0-7
svn export $SVN/dxp/tags/R3-1 dxp-3-1
svn export $SVN/ip/tags/R2-13 ip-2-13
svn export $SVN/ip330/tags/R2-7 ip330-2-7
svn export $SVN/ipUnidig/tags/R2-9 ipUnidig-2-9
svn export $SVN/love/tags/R3-2-5 love-3-2-5
svn export $SVN/mca/tags/R7-1 mca-7-1
svn export $SVN/modbus/tags/R2-3 modbus-2-3
svn export $SVN/motor/tags/R6-7 motor-6-7
svn export $SVN/optics/tags/R2-8-1 optics-2-8-1
svn export $SVN/quadEM/tags/R2-6 quadEM-2-6
svn export $SVN/softGlue/tags/R2-2 softGlue-2-2
svn export $SVN/sscan/tags/R2-7 sscan-2-7
svn export $SVN/std/tags/R3-1 std-3-1
svn export $SVN/stream/tags/R2-5-1 stream-2-5-1
svn export $SVN/vac/tags/R1-4 vac-1-4
svn export $SVN/vme/tags/R2-8 vme-2-8
svn export $SVN/vxStats/tags/R1-7-2h vxStats-1-7-2h
svn export $SVN/xxx/tags/R5-6 xxx-5-6
# other directories
svn export $SVN/configure/tags/synApps_5_6 configure
svn export $SVN/utils/tags/R5-6 utils
svn export $SVN/documentation/tags/synApps_5_6 documentation


# get allenBradley-2-2 from ?
svn export https://svn.aps.anl.gov/epics/asyn/tags/R4-18 asyn-4-18
svn export https://svn.aps.anl.gov/epics/ipac/tags/V2-11 ipac-2-11
# get seq-2-1-2 from http://www-csr.bessy.de/control/SoftDist/sequencer
# get devIocStats-3-1-6 from http://www.slac.stanford.edu/grp/cd/soft/epics/site/devIocStats/
