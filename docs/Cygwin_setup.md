---
layout: default
title: Cygwin Notes
nav_order: 7
---


Building synApps on Cygwin
==========================

The following components from the Cygwin distribution package are required in order to build synApps for the cygwin-x86_64 architecture: 
- base 
    - All default components
- devel 
    - gcc-core
    - gcc-g++
    - libncurses-devel
    - make
    - readline
- interpreters 
    - perl
- libs 
    - ncurses
    - sunrpc

To set up the PATH and EPICS\_HOST\_ARCH environment variables create a script file called /usr/local/bin/setup\_epics containing lines like the following: 
```
export PATH="/usr/bin:/usr/local/bin:/path/to/epics/base/bin/cygwin-x86_64"
export EPICS_HOST_ARCH=cygwin-x86_64
```

The last element in the PATH definition must be the path to the bin/cygwin-x86_64 subdirectory in your local installation of EPICS base. When logging in to the bash shell on cygwin type the command

```
source setup_epics
```

to execute that script.
