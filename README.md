# support
APS BCDA synApps module: support

For more information, see  
    http://epics-synapps.github.io/support/
    
converted from APS SVN repository: Fri Nov 20 18:28:17 CST 2015

Regarding the license of tagged versions prior to synApps 4-5,
refer to http://www.aps.anl.gov/bcda/synApps/license.php


## Install synApps from github source

```
# 1. download the installer script
wget https://github.com/EPICS-synApps/assemble_synApps/releases/download/R6-2-1/assemble_synApps

# 2. Make it executable
chmod a+x assemble_synApps

# 3. Run assemble_synApps, giving it the location of your installation of EPICS base
assemble_synApps --base=/path/to/base

# 3. (optional) Specify the (new) directory name where synApps will be installed.
#    synApps is the default
#    This directory will be created when assemble_synApps.sh is run.
assemble_synApps --base=/path/to/base --dir=synApps_my_version

```


## Download synApps from tarball

Tarballs are provided in the github tagged releases:

https://github.com/EPICS-synApps/support/releases
