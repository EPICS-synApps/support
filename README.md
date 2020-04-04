# support
APS BCDA synApps module: support

For more information, see
   http://www.aps.anl.gov/bcda/synApps

converted from APS SVN repository: Fri Nov 20 18:28:17 CST 2015

Regarding the license of tagged versions prior to synApps 4-5,
refer to http://www.aps.anl.gov/bcda/synApps/license.php


## Download the synApps modules

```
# 1. download the installer script
wget https://raw.githubusercontent.com/EPICS-synApps/support/master/assemble_synApps.sh

# 2. edit assemble_synApps.sh for your version of EPICS base and local directory paths

# 3. (optional) Specify the (new) directory name where synApps will be installed.
#    This is the default:
#    export SYNAPPS_DIR=synApps
#    This directory will be created when assemble_synApps.sh is run.

# 4. download & install the synApps source files:
bash ./assemble_synApps.sh
```
