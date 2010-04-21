#!/bin/csh
setenv SVN https://subversion.xor.aps.anl.gov/synApps
mkdir synApps_5_5
cd synApps_5_5
svn export $SVN/support/tags/synApps_5_5 support
cd support
# modules
svn export $SVN/areaDetector/tags/synApps_5_5 areaDetector-s55
svn export $SVN/autosave/tags/R4-6 autosave-4-6
svn export $SVN/busy/tags/R1-3 busy-1-3
svn export $SVN/calc/tags/R2-8 calc-2-8
svn export $SVN/camac/tags/R2-6 camac-2-6
svn export $SVN/dac128V/tags/R2-6 dac128V-2-6
svn export $SVN/delaygen/tags/R1-0-5 delaygen-1-0-5
svn export $SVN/dxp/tags/synApps_5_5 dxp-s55
svn export $SVN/ip/tags/R2-10 ip-2-10
svn export $SVN/ip330/tags/R2-6 ip330-2-6
svn export $SVN/ipUnidig/tags/R2-7 ipUnidig-2-7
svn export $SVN/love/tags/R3-2-4 love-3-2-4
svn export $SVN/mca/tags/synApps_5_5 mca-s55
svn export $SVN/modbus/tags/R2-0 modbus-2-0
svn export $SVN/motor/tags/R6-5 motor-6-5
svn export $SVN/optics/tags/R2-7 optics-2-7
svn export $SVN/quadEM/tags/R2-4-1 quadEM-2-4-1
svn export $SVN/softGlue/tags/R1-0 softGlue-1-0
svn export $SVN/sscan/tags/R2-6-6 sscan-2-6-6
svn export $SVN/std/tags/R2-8 std-2-8
svn export $SVN/stream/tags/R2-4-1 stream-2-4-1
svn export $SVN/vac/tags/R1-3 vac-1-3
svn export $SVN/vme/tags/R2-7 vme-2-7
svn export $SVN/vxStats/tags/R1-7-2h vxStats-1-7-2h
svn export $SVN/xxx/tags/R5-5 xxx-5-5
# other directories
svn export $SVN/configure/tags/synApps_5_5 configure
svn export $SVN/utils/tags/R5-5 utils
svn export $SVN/documentation/tags/R5-5 documentation


# get allenBradley-09092009 from ?
svn export https://svn.aps.anl.gov/epics/asyn/tags/R4-13 asyn-4-13
svn export https://svn.aps.anl.gov/epics/ipac/tags/V2-11 ipac-2-11
# get seq-2-0-12 from http://epics.web.psi.ch/software/sequencer/
