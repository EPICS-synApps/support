---
layout: default
title: Overview
nav_order: 2
---


synApps 6.2.1
=============

Table of Contents
=================

- [Introduction](#Introduction)
- [Contents](#Contents)
- [How to deploy synApps](<#How to deploy synApps>)
- [How to build synApps](<#How to build synApps>)
- [How to make synApps work](<#How to make synApps work>)
- [How to extend synApps](<#How to extend synApps>)
- [The synApps utils directory](<#The synApps utils directory>)
- [Appendix](#Appendix)


Introduction
------------

- - - - - -

synApps is a collection of [EPICS](https://epics.anl.gov/) software intended to support most of the common requirements of an x-ray laboratory or synchrotron-radiation beamline. Because it is EPICS software, synApps is extensible by developers and end users, to support new devices and experimental techniques. This extensibility frees synApps to focus mostly on general-purpose capabilities and infrastructure, from which application-specific software can be built or assembled.

> Thus, for example, synApps provides support for motors, scalers, and scans, but it does not tie those items together into an immediately executable scan (of specific motors, to acquire specific scaler channels, for a specific dwell time, etc.). The user does this at run time (or a knowledgeable user can provide a fully specified scan, and give the novice user a button to start it).
> 
> Similarly, synApps provides support for ADC's and PID loops, but somebody has to tell the PID software what feedback value to read, what conditioning function to run it through, what PID parameters to use, and what actuator to drive. By default, all of these choices can be made at top level, by the end user. Or, a knowledgeable user can provide a fully specified PID loop, and make it available to a novice user through a simplified or otherwise customized interface. The techniques and tools used to accomplish this are essentially the same as those a user would have applied at run time, so the packaged solution can be prototyped and tested at run time.

synApps is organized into modules, whose structure is based on the example directory tree produced by the EPICS application, `makeBaseApp.pl`, typically with two additional directories: a documentation directory, and a display-file directory. synApps modules typically contain source code, EPICS databases and database-definition files, autosave-request files, client scripts, display files, libraries and executables, and documentation.

Most synApps modules are intended primarily to export support to other modules. Some synApps modules produce bootable software, in addition to support software, but in most cases, this bootable software is primarily for testing, and for demonstrating how the support software can be used. The support exported by a module is of the following types, with example names and locations from the __calc__ module:

> a database-definition file, in calc/dbd
* `calcSupport.dbd`  
> a linked library, in calc/lib/&lt;arch&gt 
* 'libcalc`
> header files, in calc/include 
* `transformRecord.h`  
> database files, and associated autosave-request files, in calc/calcApp/Db 
* `userTransforms10.db`
* `userTransforms10_settings.req`  
> display files, in calc/calcApp/op/adl, calc/calcApp/op/ui, and calc/calcApp/op/opi 
* `userTransforms10.adl`  
* `userTransforms10.ui`  
* `userTransforms10.opi`  


One synApps module, the __xxx__ module, is different: it doesn't export anything. It imports support from other modules, and produces bootable software to support an EPICS *IOC*. The __xxx__ module is documentation in runnable form, and also a template from which a synApps application can be constructed. __xxx__ is not comprehensive: it doesn't apply all of synApps; it's usually a little behind the rest of synApps; it focuses more on VME crates than on other kinds of IOCs; and it's a compromise between what is most widely used and what is most likely to build and run out of the box. 
> *If you haven't run into the term 'IOC' yet, two things: 
> 1. IOC stands for Input/Output Controller. Initially, this was a VME crate with a processor running EPICS under the VxWorks operating system, but beginning with EPICS 3.14, an EPICS IOC can also be a set of tasks on a workstation running Linux, Windows, Cygwin, Solaris, RTEMS, Mac OS, and, no doubt, other operating systems.
> 2. The [](https://epics.anl.gov/base/R3-15/6-docs/AppDevGuide/AppDevGuide.html)* EPICS Application Developer's Guide *is an essential reference for anyone planning to develop or deploy EPICS software. While you won't need to read the guide to build or run synApps, you will need it to understand what you've done, to diagnose problems, and to extend synApps in any significant way.*


Contents
--------

- - - - - -

Here's a list of the __modules__ and *directories* in synApps:

| __Module__/*directory* | __description__ |
|---|---|
| __alive__ | Support for collecting, maintaining, and displaying status information about a collection of EPICS IOCs. |
| __areaDetector   ADcore   ADSupport   ADSimDetector__ | Support for cameras and other 2D detectors. areaDetector consists of some core modules, and many detector-specific modules; synApps contains only the top-level directory, *areaDetector*, and the modules *ADCore*, *ADSupport*, and *ADSimDetector*. See [areaDetector](https://github.com/areaDetector) for more information |
| __autosave__ | Support for saving software parameters at run time, and restoring them during the next reboot. Autosave also provides a way to manage collections of PV values at runtime (*configMenu*), and a way to initialize array PV's at boot time. |
| __busy__ | The busy record, which allows developers more ways to indicate when an operation is complete. |
| __calc__ | Run-time expression evaluation, derived from the calcout record in EPICS base, and extended to operate on strings, arrays, and to implement coupled expressions. |
| __caputRecorder__ | Support for recording a series of caputs as a python function, and replaying the series. |
| __camac__ | Support for CAMAC hardware. |
| *configure* | Build files |
| __dac128V__ | Support for an IndustryPack DAC module. |
| __delaygen__ | Support for delay generators, including the SRS DG645, Colby Instruments PDL100A, and Gigabaudics PADL3. |
| *documentation* | Um... documentation |
| __dxp__ | Support for X-Ray Instrumentation Associates's DXP digital signal processor |
| __dxpSITORO__ | Support for XIA SITORO based FalconX spectrometers |
| __galil-3__ | Support for Galil motor controllers |
| __ip__ | Support for various serial, and other message-based, devices. |
| __ip330__ | Support for an IndustryPack ADC module |
| __ipUnidig__ | Support for an IndustryPack digital I/O module |
| __labjack__ | Support for LabJack I/O modules |
| __love__ | Support for Love controllers |
| __lua__ | Support for Lua scripting language features |
| __mca__ | Support for multichannel analyzers and multichannel scalers. |
| __measComp__ | Support for USB I/O modules from [Measurement Computing](http://www.mccdaq.com) |
| __modbus__ | Support for ModBus-protocol devices over TCP, serial RTU, and serial ASCII links |
| __motor__ | Support for motors |
| __optics__ | Support for optical tables, monochromators, slits, etc. |
| __quadEM__ | Support for an APS-developed 4-channel electrometer |
| __softGlue__ | Support for user-programmed "wiring" of custom FPGA content loaded into an Acromag IP-EP201 module. |
| __softGlueZynq__ | Support for user-programmed "wiring" of custom FPGA content loaded into a Xilinx Zynq board. |
| __sscan__ | Support for scans (programmed control and data acquisition). |
| __std__ | Miscellaneous EPICS support, including the epid (extended PID), scaler, sseq (string sequence), and timestamp records; and pvHistory support. |
| __stream__ | Dirk Zimoch's streamDevice, in a module-flavored wrapper. |
| *utils* | Miscellaneous tools, including support for converting an application from one version of synApps to another; support for the MDA file format, written by the __sscan__ module; and support for EPICS-application prototyping. |
| __vac__ | Support for vacuum controllers |
| __vme__ | Support for VME hardware |
| __xspress3__ | Support for Quantum Detectors Xpress3 Hardware |
| __xxx__ | Sample user-application directory |
| __Yokogawa\_DAS__ | Support for the Yokogawa MW100 Digital Acquisition Unit. |

See support/configure/RELEASE for a complete set of compatible module versions. This release of synApps is compatible with EPICS 3.15 (and above) releases, vxWorks 6.9, and the following EPICS modules, which are produced and maintained by other members of the EPICS collaboration. These modules are not part of synApps, but their maintainers have permitted us to distribute copies along with synApps:

| Module | description |
|---|---|
| __allenBradley__ | for communicating with Allen Bradley PLC's (ANL) |
| __ipac__ | required for IndustryPack support (ANL) |
| __asyn__ | required by many modules (ANL) |
| __seq__ | for SNL programs in synApps (BESSY)   source: http://www-csr.bessy.de/control/SoftDist/sequencer |
| __stream__ | configurable device support for message-based devices (PSI)   source: https://github.com/paulscherrerinstitute/StreamDevice |
| __devIocStats__ | IOC statistics, replaces vxStats (SLAC)   source: http://www.slac.stanford.edu/grp/cd/soft/epics/site/devIocStats/ |

> Previous versions of synApps included and relied on the __genSub__, __ccd__, and __pilatus__ modules. Beginning with EPICS 3.14.10, a replacement for the genSub record, called the aSub record, is included in base, and synApps has been modified to use it instead of the genSub record. The __ccd__ and __pilatus__ modules have been replaced by the __areaDetector__ module.

For convenience, this distribution includes the modules listed above, in place and ready to build, with minor modifications to build files. A few of the modules have suffered more substantial modifications to fix problems, add display files, etc.

synApps includes software developed by the Beamline Controls &amp; Data Acquisition, Software Services, and Accelerator Controls groups of the Advanced Photon Source (APS); by developers in APS Collaborative Access Teams – notably, Mark Rivers (CARS-CAT); and by developers in the EPICS collaboration outside of the APS – notably, those at the Diamond Light Source, the Berliner Elektronenspeicherring-Gesellschaft fÃ¼r Synchrotronstrahlung (BESSY), the Stanford Linear Accelerator Center (SLAC), the Swiss Light Source (SLS)/Paul Scherrer Institut (PSI), the National Synchrotron Light Source (NSLS), the Deutsches Elektronen Synchrotron (DESY), the Spallation Neutron Source (SNS), the Australian Light Source, and the Canadian Light Source.

Aside from EPICS databases, SNL (State Notation Language) programs, and the like, synApps contains the following code:

- ### Record support in or distributed with synApps
    
    | Record | Description |
    |---|---|
    | __ab\*__ | AllenBradley-module custom records |
    | __alive__ | Send IOC status to a central server. |
    | __acalcout__ | calcout record extended to handle array expressions |
    | __asyn__ | provide access to nearly all of the features of the asyn facility |
    | __busy__ | utility record: calls recGblFwdLink only when its VAL field is zero, allowing CA clients, and asyn drivers to participate in EPICS putNotify (ca\_put\_callback()) operations |
    | __camac__ | camac-module custom record |
    | __digitel__ | vac-module custom record |
    | __epid__ | Extended version of the PID record, previously in EPICS base. Intended for implementing feedback loops |
    | __luascript__ | Record with scriptable behavior |
    | __mca__ | support for multichannel analyzers, and some other array-valued detectors |
    | __motor__ | stepper and servo motors, "soft" motor |
    | __scalcout__ | calcout record extended to handle string expressions, links, and values |
    | __scaler__ | scaler bank |
    | __sscan__ | Replaces the scan record (Ned Arnold/APS) previously in EPICS base. This version uses a modified version of recDynLlib that supports dbNotify command completion. It uses ca\_put\_callback to do puts, instead of ca\_put. |
    | __scanparm__ | scan parameters for use with the scan record |
    | __sseq__ | string-sequence record. This is a modified version of the seq record in base. This version can link to/from either string or numeric PVs, and it can use dbCaPutLinkCallback to wait for completion of the execution started by one link before going on to the next. |
    | __swait__ | replaces the wait record previously in EPICS base. This version uses a modified version of recDynLlib that supports dbNotify command completion. It uses ca\_put\_callback to do puts, instead of ca\_put. |
    | __table__ | 6-degree-of-freedom optical table |
    | __transform__ | like an array of calc records, with output links |
    | __vme__ | generic vme record (Mark Rivers/APS/CARS-CAT) |
    | __timestamp__ | (written by Stephanie Allison/SLAC) Needed by the vxStats module, but apparently not available in a published module. |
    | __vs__ | vac-module custom record |
- ### Device support in or distributed with synApps
    
    List appended to this document.
- ### Other C code
    
    aCalcPostfix, aCalcPerform sCalcPostfix, sCalcPerform 
    * Support for run-time expression evaluation 
    recDynLink 
    * Backward compatible extension of the dynamic-link software previously in EPICS base. (New code should probably use dbCaPutlinkCallback(), instead of recDynLink.) 
    autosave (save\_restore, dbrestore, configMenu, asVerify, autosaveBuild) 
    * Automatic parameter save and boot-time restore. Run-time management of collections of PV values. 
    saveData 
    * Saves scan data to files on an NFS-mounted disk (vxWorks), or to a local disk (other operating systems). 
    luascript 
    * Support for running scripts to control the value of standard records
    
- ### Documentation
    
    In addition to this top-level documentation, synApps modules have their own documentation directories, and the __xxx__ module contains examples of how much of the software is imported, built, loaded, and run. Some modules have their own example iocBoot directories.
- ### Miscellaneous
    
    The synApps support/utils directory contains a variety of scripts, programs, etc., that some have found useful. See [The synApps utils directory](<#The synApps utils directory>) for details.


How to deploy synApps
---------------------

Although synApps is distributed as a single 'support' directory, it's normally deployed as a two-part system: a 'support' directory, and one or more 'user' directories. The support directory can be installed on a read-only file system, along with EPICS base and other modules, and used from there by user directories, each of which typically begins as a copy (or a collection of copies) of the __xxx__ module, and is customized/extended to suit a particular application and set of hardware.

I'm not being very precise about what is meant by a user directory, because there are a number of reasonable variations. At the simplest, a single copy of the __xxx__ module, which supports a single IOC, is a user directory. If several IOC's cooperate to serve a single application (such as a synchrotron beamline), one might make several independent copies of __xxx__, or one might extend a single __xxx__ copy to contain multiple xxxApp directories, and multiple iocBoot/iocxxx directories. At APS, the BCDA group maintains around 100 top-level user directories (for each version of synApps) each of which contains a number of copies of __xxx__, and most of which, in turn, contain multiple xxxApp and iocBoot/iocxxx directories.

Here's what a complete installation might look like (much detail omitted) with all the files you will have to edit before you can build or boot an IOC:

####  The support directory

```

synApps_X_X/support/
    Makefile
    alive/
    allenBradley/
    areaDetector/
    asyn/
    busy/
    calc/
    camac/
    caputRecorder/
    configure/
        CONFIG
        CONFIG_SITE                     <— EDIT to build
        RELEASE                         <— EDIT to build
        EPICS_BASE.<arch>               <— EDIT to build for <arch>
        Makefile
        RELEASE
        SUPPORT.<arch>                  <— EDIT to build for <arch>
        ...
    dac128V/
    delaygen/
    devIocStats/
    documentation/
    dxp/
    ip/
    ip330/
    ipUnidig/
    ipac/
        drvIpac/drvIpac.dbd             <— EDIT to build
    love/
    mca/
    measComp/
    modbus/
    motor/
        motorApp/
            Makefile                    <— EDIT to build
    optics/
    quadEM/
    seq/
    softGlue/
    sscan/
    std/
    stream/
    utils/
    vac/
    vme/
    xxx/

```

####  The user-directory tree

```

synApps_X_X/ioc/
    1bm/
        Makefile
        bin/
        configure/
            CONFIG_SITE                 <— EDIT to build
            RELEASE                     <— EDIT to build
        dbd/
        iocBoot/
            Makefile
            nfsCommands                 <— EDIT to run
            accessSecurity.acf          <— EDIT to run
            ioc1bma/
                Makefile                <— EDIT to build
                *.cmd
                *.req
                *.substitutions
                autosave/
                cdCommands or envPaths
            ioc1bmb/
            ioc1bmc/
            ioc1bmd/
                <much like ioc1bma>
        release.pl
        setup_epics_common              <— EDIT to run user interface
        start_MEDM_1bma                 <— EDIT to run user interface
        start_MEDM_1bmb                 <— EDIT to run user interface
	start_MEDM_1bmc                 <— EDIT to run user interface
	start_MEDM_1bmd                 <— EDIT to run user interface
        start_putrecorder               <— EDIT to use caputRecorder
        1bmaApp/
        1bmbApp/
        1bmcApp/
        1bmdApp/

    1id/
    2bm/
    2id/
    ...
        <much like 1bm>
```

As shown above, the following files can or must be edited to modify the way the synApps support directory is built. After modifying files in the support, or support/configure directories, you should run `make release`, and `make rebuild`, in the support directory.

> `support/configure/RELEASE` 
* Edit the definitions of `EPICS_BASE` and `SUPPORT` with the correct paths to these directories on your system. Comment out any modules you don't want to build. 
> `support/configure/EPICS_BASE.<arch>` 
* If you plan to build on more than one host architecture from a single synApps directory, and the hosts use different paths to refer to the same file (for example, Windows and Linux using a shared file system) then you can override the definition of `EPICS_BASE` in the `RELEASE` file by specifying host-specific paths to base in separate `EPICS_BASE.<arch>` files. If you don't have such plans, then you can delete these files, but if they exist, they must be correct. 
> `support/configure/SUPPORT.<arch>` 
* Similar to `EPICS_BASE.<arch>`, but for the synApps `support` directory 
> `support/configure/CONFIG_SITE` 
* Edit to set the following variables, which control what will be built: The supported values for these variables are `YES` and `NO`.  
> `LINUX_USB_INSTALLED` 
* This controls the build of the __dxp__ module. If usb is not installed for developers, then parts of dxp/dxpApp/handelSrc will not be built, and the example application executable, dxpApp, will not be built, so dxp/iocBoot cannot be used. 
> `LINUX_NET_INSTALLED` 
* This controls the build of the __mca__ module, specifically, support for the Canberra AIM hardware. 
> `IOCS_APPL_TOP` 
* Path to application top as seen by IOC. Set this when your IOC and host use different paths to access the application directory. This will be needed to boot from a Microsoft FTP server or with some NFS mounts. You must rebuild in the iocBoot directory for this to take effect. 
> `support/ipac/<version>/drvIpac/drvIpac.dbd` 
* uncomment `registrar()` commands for IndustryPack carriers you plan to use. 
> `support/motor/<version>/motorApp/Makefile` 
* comment or uncomment to select the motor support you want to build.

The following files must be edited before building a user directory:

> `ioc/<appname>/configure/RELEASE`  
* edit the definition of `SUPPORT` with the correct path to the support directory 
> `ioc/<appname>/iocBoot/<iocname>/Makefile`  
* edit to specify the architecture that is to be built

The following files must be edited before running the user interface:

> `ioc/setup_epics_common`  
* set the value of Channel Access variables, such as EPICS\_CA\_MAX\_ARRAY\_BYTES. 
> `ioc/start_***_xxx`  
* edit to specify the path to the application and display-file directories, and the name of the top-level display file. 
> `ioc/start_putrecorder`  
* edit to specify the path to the application and its python directory, and to specify the ioc prefixe(s) to monitor.

The association between a user directory, and the support directory on which it depends, is made entirely by the file, configure/RELEASE, in the user directory. Typically, this file simply includes the configure/RELEASE file from the support directory, but it may differ: it may specify EPICS modules not included in synApps, for example. Or, if the support directory contains more than one built version of a module (the original and a bug fix, for example) the user directory can choose which version it will use.

> *Note, however, that the modules in synApps are interdependent. Many of the modules depend on the __asyn__ module, for example, and there are many other dependencies, both direct and implied. (If module __a__ depends on module __b__, and module __b__ depends on module __c__, then __a__also depends on __c__, and it must specify the same version of __c__ that __b__ specifies.) The complete set of modules selected by a user directory must be self consistent, and the EPICS build will ensure this, unless you tell it not to, by defining 

```
CHECK_RELEASE=NO
```

or 

```
CHECK_RELEASE=WARN
```
 
in `ioc/configure/CONFIG_SITE`.*

For completeness, the format of a RELEASE-file path definition is "`<name>=<path>`", where &lt;name&gt; is an arbitrary string, and &lt;path&gt; is an absolute directory name (starts with '/' on a unix host, or with a drive name such as 'C:' on Windows). Although &lt;name&gt; is arbitrary, you should be consistent. Generally, the EPICS build doesn't care what paths are named, because it's just going to collect them all into a list, and use the list to search for libraries, .dbd files, etc. But, in the module consistency check mentioned above, the name does matter, because EPICS can't check that all modules in a build are using the same version of, say, the asyn module, unless they all use the same &lt;name&gt; for it. Also, in the xxx module, &lt;name&gt; is used extensively to find display files (that is, to set the EPICS\_DISPLAY\_PATH environment variable), and to specify databases, autosave request files, etc., when an ioc is booting.

The synApps build imposes an additional constraing on module names. Because synApps uses EPICS build rules to descend from `support` into the modules, module names may not include the character '.'. (The EPICS build rules expect '.' to be followed by a host or target architecture.) <a name="How to build synApps"></a>



How to build synApps
--------------------


1. System configuration Before building synApps, you should ensure that your system has the tools, libraries, header files, etc. required to build the modules you want to build. Here's a list of dependencies we've documented so far.
    
    > *Please help: new users are particularly well placed to help us complete this list. Long-time developers typically have lots of things correctly configured that they don't even remember configuring.*
    
    
    - The EPICS extension, [msi](http://www.aps.anl.gov/epics/extensions/msi/index.php), version 1-5 or higher. If attempting to build with EPICS base 3.14, this tool is needed to build some softGlue databases, EPICS base 3.15 and above include this as part of base.
    - Linux: libusb.a, and associated header filesneeded for the __dxp__ module
    - Cygwin: Cygwin is configured from a menu of choices organized by function. You will need the following components from the following menu headings:
        
        
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
            - sunrpc (needed for the __asyn__ and __sscan__ modules). In cygwin 1.7, rpc was replaced by libtirpc: instead of linking with librpc, you link with libtirpc. EPICS base 3.14.12.1 defines CYGWIN\_RPC\_LIB (configure/os/CONFIG.Common.cygwin-x86) to handle this.
        - misc 
            - DLPORTIO (needed for the __dxp__ module)
            - the sequencer (version 2.1) uses re2c, which is not a standard part of cygwin. You must install re2c version 0.13.3 or higher. This is available from http://re2c.org/.
    - Windows: DLPORTIOneeded for the __dxp__ module
2. Building and configuring the support directory If you have a built copy of EPICS base 3.14.12.4 or later, then building the synApps support directory should be very simple:
    
    
    1. Edit support/configure/RELEASE, and support/configure/CONFIG\_SITE, as noted above.
    2. Edit support/configure/EPICS\_BASE.&lt;arch&gt;, support/configure/SUPPORT.&lt;arch&amp;gt, as noted above, for the architectures you want to build.
    3. Edit ipac/&lt;version&gt;/drvIpac/drvIpac.dbd, and motor/&lt;version&gt;/motorApp/Makefile, as noted above.
    4. Set the environment variable `EPICS_HOST_ARCH` to the architecture (and compiler, if there is a choice) on which you are building. synApps is tested with the architectures `linux-x86_64`, `win32-x86`, and `win64-x86`.
    5. In support, run '`make release`'. (See note below.)
    6. In support, run '`make`'. (You should be able to use '`make -j`' to build synApps more quickly.)
    
    You should use the same GNU Make executable that was used to build EPICS base. You may need `$(EPICS_BASE)/bin/<arch>` in your path, and you may need `$(EPICS_BASE)/lib/<arch>` in `LD_LIBRARY_PATH`.
    
    When executed in the support directory, '`make release`' will go to all of the modules `support/Makefile` is configured to build, and edit the `configure/RELEASE` files in those modules so that they all build from the same versions of EPICS base and other known modules.
    
    Typically, the build will not succeed the first time, because you will not have all of the required system support. If you find that you cannot build some synApps module, you can disable its build by commentng it out of `support/configure/RELEASE`.
3. Building and configuring a user directory Once synApps' support directory has built without errors, the __xxx__module will have been configured (`xxx/configure/RELEASE` will have correct, absolute paths to base and support) and built, so you can use it as an example – or, better, a template – for constructing user directories to support your IOCs. To make a template of xxx, clean and uninstall it, and tar a copy of the directory. To use the template, untar it, cd to its top-level directory and run `support/utils/changePrefix` to change the PV-name prefix from xxx to whatever you want. (Note you must have `support/utils` in your command path, or you could copy `support/utils/changePrefix` and `support/utils/doSed` to a directory that is in your command path. Note that `changePrefix` is synApps-version specific.)
    
    Here's what I do:
    
    ```
    
    	# Do once when synApps is built:
    	cd $(SYNAPPS)/support/xxx
    	setenv EPICS_HOST_ARCH <host architecture>
    	make clean uninstall
    	(repeat as needed for any other architectures)
    	tar cvf ../xxx.tar *
    
    	# Do whenever a new user directory ('1bm', in this example) is needed:
    	cd $(SYNAPPS)/ioc
    	mkdir 1bm
    	cd 1bm
    	tar xf $(SYNAPPS)/support/xxx.tar
    	changePrefix xxx 1bma
    	mv iocBoot/iocvxWorks iocBoot/ioc1bma
    	edit iocBoot/ioc1bma/Makefile to specify the IOC processor type
    	make
    ```
    
    To put a second application, 1bmb, into 1bm, I run the following commands:
    
    ```
    
    	cd $(SYNAPPS)/ioc
    	mkdir temp
    	cd temp
    	tar xf $(SYNAPPS)/support/xxx.tar
    	changePrefix xxx 1bmb
    	mv iocBoot/iocvxWorks iocBoot/ioc1bmb
    	edit iocBoot/ioc1bmb/Makefile to specify the ioc processor type
    	cd $(SYNAPPS)/ioc
    	mv temp/1bmbApp/start_epics_1bmb 1bm
    	mv temp/1bmbApp 1bm
    	mv temp/iocBoot/ioc1bmb 1bm/iocBoot
    	rm -rf temp
    	cd 1bm
    	make
    ```
    
    Edit the files above to agree with your hardware, to load the databases you want, etc., set up the IOC processor's parameters to load from the software just configured, and boot the crate. If you don't know how to do this, read on.



How to make synApps work
------------------------



1. Setting up the IOC (vxWorks) Ensure that `$(EPICS_BASE)/bin/<arch>/caRepeater` gets run when your workstation boots. If you have no way of doing this, you can run it manually or put the command in your .login file.
    
    Setup your host system to work with the EPICS processor. See the *VxWorks Programmer's Guide* if you have a copy. Here's what we do (on a Sun workstation):
    
    
    - Add a user named `<vx_username>` with the password `<vx_password>`. The user has nothing in its home directory, and very few priviledges.
    - Connect an ethernet cable to the processor.
    - Setup the workstation to use a serial port at 9600 baud. Connect a serial cable from the workstation to the VME processor's "Console" port.
    - Start up an "xterm" on the workstation and type 
    ```
    cu -lttya
    ```
        
        (On some workstations we must type "`cu -lcua/a`".) This gets the xterm communicating with the crate processor.
    - Turn the crate on. The crate processor says "Press any key to stop auto-boot..." and a number counting down from 7. Pressing a key gets the prompt "\[VxWorks Boot\]:"
    - Type "p" to see the current boot parameters, type "c" to change them. Here are sample boot parameters 
    ```
            boot device          : dc 
            processor number     : 0 
            host name            : <server> 
            file name            : /usr/local/vxWorks/T222/mv2700-asd1
            inet on ethernet (e) : xxx.xxx.xxx.xxx:fffffe00 
            inet on backplane (b): 
            host inet (h)        : xxx.xxx.xxx.xxx
            gateway inet (g)     : 
            user (u)             : <vx_username> 
            ftp password (pw) (blank = use rsh): <vx_password>  
            flags (f)            : 0x0
            target name (tn)     : iocxxx
            startup script (s)   : /home/server/USER/epics/xxx/iocBoot/iocxxx/st.cmd
            other (o)            : 
        ```
    
    See `support/xxx/iocBoot/ioc*/bootParms` for other processor types. If your VME processor has mount access to an 'APSshare' NFS file server, you can specify the 'file name', above, as "/APSshare/vw/T222/mv2700-asd1".
2. Display files synApps includes hundreds of display files intended for use with the EPICS display manager, MEDM, and translations of those files that work with CSS-BOY and caQtDM. Other EPICS display managers exist, and I once did a mass automated translation of MEDM display files to the EDM display manager's file format, using software developed by others. This translation was only partially satisfactory, but we don't have the resources to do the job better or more generically. In this documentation, I'll limit attention to MEDM display files.
3. Fitting synApps to an application This happens in the user directory. Generally, you must tell "EPICS" what hardware is in your crate, and what addresses, interrupt vectors, etc. you have set your hardware to use. (See support/xxx/documentation/vme\_address.html for a list of suggested values.) You also must specify which motors any slit, table, monochromator, etc., control software is to use. If you use serial or GPIB, you must match port names to hardware devices, set serial-port parameters, and specify GPIB addresses. For any IndustryPack modules, you must specify the IP carrier and slot into which you've loaded those modules.
    
    __Overview__
    
    In a complete job of fitting synApps to an IOC's hardware, all of the following files will be touched:
    
    > `xxx/iocBoot/ioc*/st.cmd.*`
    * This is the ioc's startup script, and it loads the other .cmd files 
    > `xxx/iocBoot/ioc*/examples/*.iocsh`  
    * Example command files that can be invoked by st.cmd
    > `xxx/iocBoot/ioc*/substitutions/*.substitutions`
    > 'xxx/iocBoot/ioc*/auto_positions.req`  
    * `xxx/iocBoot/ioc*/auto_settings.req`specifies PV's to be saved periodically during operation, and restored automatically when the ioc is rebooted. (But note that you can have these files constructed for you during the boot process. See [autosaveBuild](https://htmlpreview.github.io/?https://github.com/epics-modules/autosave/blob/R5-10/documentation/autoSaveRestore.html#autosaveBuild) in the autosave documentation.) `xxx/iocBoot/ioc*/saveData.req`identifies PV's used by the saveData software, sscan records to be monitored for data, and PV's whose values are to be included in all scan-data files. `xxx/iocBoot/ioc*/bootParms`a copy of the boot parameters (in case the IOC processor crashes in a way that erases nonvolatile memory)
    
    __In more detail__
    
    
    - `xxx/iocBoot/ioc*/st.cmd.*`This is the file run by the IOC at boot time. It loads an executable built in the IOC directory (e.g., `xxx`, or `xxx.munch`), sets parameters to configure that software, makes calls to that software to configure it for a particular set of hardware, and loads databases from synApps modules. Mostly, it sources ioc shell files that do these same things.
        
        This file, and the files it sources, are probably worth studying. They are reasonably well commented, and contain `dbLoadRecords()` commands for most of the EPICS databases in synApps.
    - Motors To load more motors, add lines to the file `xxx/iocBoot/ioc*/motor.substitutions`. For motors controlled by a VME board, edit `vme.cmd` to specify the hardware address, etc. For motors controlled through a serial connection, edit `serial.cmd`.
        
        If you want the new motors to work with the 'AllStop' button (`xxx:allstop.VAL`– see the top-level MEDM display `xxx.adl`), load the database `$(MOTOR)/db/motorUtil.db`, and run the command `motorUtilInit("xxx:")`.
        
        If you want the IOC automatically to save positions and settings of the new motors, and restore them when the crate reboots, add lines to the files `xxx/iocBoot/ioc*/auto_settings.req` and `xxx/iocBoot/ioc*/auto_positions.req`.
    - Slits To use a pair of motors to control a slit, search for `2slit.db`in `xxx/iocBoot/ioc*/examples/optics.iocsh`, and edit the `dbLoadRecords()` command you'll find there. The example in `optics.iocsh` loads two copies of `2slit.db` intended for use as the horizontal and vertical members of a four-jaw slit. The MEDM displays `2slit*.adl` and `4slit*.adl` are involved in these applications.
        
        The slit database can make either of two sets of assumptions about the two motors attached to the individual slit leaves, depending on the value of the macro "RELTOCENTER" that may be supplied when loading the 2slit.db database.
        
        If "RELTOCENTER=0" is supplied, or if RELTOCENTER is omitted altogether:
        
        
        - Both motors have the same engineering units.
        - Both motors are in the same coordinate system. When the center position is increased, both motors' .VAL fields increase.
        - The APS standard beamline coordinate system is used. Positive Z is the beam direction; positive Y is upward; positive X is outward from the storage ring.
        
        If "RELTOCENTER=1" is supplied:
        
        
        - Both motors have the same engineering units.
        - Their .VAL fields increase as the slit opens.
        - The APS standard beamline coordinate system is used. Positive Z is the beam direction; positive Y is upward; positive X is outward from the storage ring.
        
        The `2slit.db` database allows users to move either the slit virtual motors or the actual motors, and it keeps all the readback values current regardless of how the actual motors got moved or recalibrated. But it does not automatically reset the slit __drive__ values when the actual motors are used. This must be done manually, using the "SYNC" button on the `2slit.adl` display. Pressing this button causes the database to read the actual motor drive values and set the slit-drive values accordingly.
        
        To recalibrate slit positions, press the "Set" button, type in the current slit position as you want it to be called, and press the "Use" button. This procedure uses the "Set" buttons of both motors the slit software talks to, and the user/dial offsets of those motors actually implement the recalibration.
        
        There is a new, experimental slit database in synApps which uses soft motor records as the user/client interface. This allows clients that know how to control a motor also to control a slit, with some limitations. We hope to use soft motor records in front of other positioners (e.g. monochromators, optical tables, insertion devices, and DAC channels) in the future.
    - Optical tables Optical tables are controlled by a custom EPICS record (the "table" record), used in the database `table.db` and controlled via MEDM displays `table*.adl`.
        
        Table virtual motors behave in much the same way as do slit virtual motors. However, the table software does not use user/dial offsets in the underlying motor to implement recalibration (it can't, since it works through a nonlinear transform). Instead, the table maintains its own offsets for all of the six coordinated motions it implements. Pressing the "Set" button causes new table positions to modify the offsets instead of moving the table (which is exactly the way motor and slit calibration works). In addition to a "Sync" button, which reads motor positions and calculates the table positions from them, the table display has an "Init" button, which zeros all offsets before doing a "sync" operation. It also has a "Zero" button, which manipulates all the table offsets to make the current table positions zero without moving or recalibrating any motors.
    - Monochromators Several varieties of crystal monochromators are supported in synApps: two constant-offset "channel-cut" monochromators, two varieties of a high-resolution four-crystal monochromator, a spherical-grating monochromator, and a multilayer monochromator. Most are supported by databases paired with State Notation Language (SNL) programs, and several MEDM displays. The EPICS databases `kohzuSeq.db`, SNL program `kohzuCtl.st`, and MEDM displays `kohzu*.adl` (also `kohzu*.gif`) are involved in control of two varieties of high-heat-load monochromators. The EPICS database `hrSeq.db`, SNL program `hrCtl.st`, and MEDM displays `hSeq*.adl` are involved in control of the high-resolution double-crystal monochromator. The spherical grating monochromator is supported by the database `SGM.db` and the displays `SGM*.adl`. The multilayer monochromator is supported by the database `ml_monoSeq.db`and displays `ml_mono*.adl`.
    - Filters The APS standard user filters combine several motors and solenoids to control the placement of filter material in the beam path. The databases `filterMotor.db` and `filterLock.db`, and the MEDM displays `*filter*.adl` are involved in this application.
        
        synApps also supports the XIA filter/shutter box, with two independently developed solutions:
        
        
        - pf4:   
            pf4\*.db  
            pf4\*.adl
        - filterbox:  
            filterBladeNoSensor.db, filterDrive.db  
            filter\_\*\_\*.adl, filterbox\_\*.adl filter\_drive\*.adl
    - Basic run-time programming Impromptu coordinated motions and other bits of run-time programming are handled by what we call a "userCalc" (actually just a swait record with a nice MEDM interface) or a "userTransform" (actually just a transform record with a nice MEDM interface). We normally load sets of these and other records into each EPICS processor, specifically for end-user programming. Users type in expressions to be evaluated, and link inputs and outputs, as needed, to glue existing objects together to do what they want done at the moment. Here are some examples of the tasks that have been accomplished with userCalcs and userTransforms:
        
        
        - Turn off hardware feedback control of a monochromator crystal when beam drops below a user-specified level. The userCalc monitored the EPICS PV that contains the value of the positron beam-current, and drove a DAC channel (used as a digital i/o bit) that enabled hardware feedback.
        - Support the ubiquitous theta/two-theta coordination by slaving the two-theta motor's .VAL field to the theta motor's .VAL field.
        - Talk to a motor through a nonlinear transformation, e.g., energy-to-Bragg-angle.
        - Close slow feedback loops – e.g., to adjust a monochromator crystal to suppress third-order diffraction through the high-heat-load monochromator.
        - Move multichannel-analyzer regions of interest automatically as the incident beam energy changes.
        - Save and automatically subtract shutter-closed offsets from scaler data.
        - Implement the first cut at support for a spherical grating monochromator.
    - String-expression support Run-time programming involving strings and/or numbers can be done with userStringCalcs, which resemble userCalcs closely, but differ in significant details. A package containing two stringCalcs and an 'asyn' record (called a "deviceCmdReply") is also available for run-time programming of simple support for serial and other message-based devices.
    - Array-expression support Run-time programming involving arrays and/or numbers can be done with userArrayCalcs, which resemble userCalcs closely, but differ in significant details.
    - Scan support Scans of up to five dimensions are supported by the `standardScans.db` database. Scan data is written to disk by the saveData program, whose user interface is contained in `saveData.db`. The number of data points per scan dimension is specified when `standardScans.db` is loaded, and is limited to 2000, unless the environment variable `EPICS_CA_MAX_ARRAY_BYTES` is specified.
        
        Note that loading `saveData.db` does not automatically cause scan data to be written to disk. You must also call the function `saveData_Init()`, specifying a scan-configuration file (`saveData.req`) which tells saveData which sscan records to monitor.
        
        Also note that initializing saveData is an all-or-nothing choice. If you initialize saveData, then *all* scans performed by sscan records named in the configuration file will be written to disk. If saveData cannot write a file, it will prevent the next scan from completing. (Scans performed by sscan records that are *not* named in `saveData.req` are completely outside of this restriction. The data they accumulate is not written to disk by saveData, so saveData is not involved in their operation.)
    - Sequence support Run-time programming of sequences is possible using the sseq record and related MEDM displays `yySseq.adl`
    - Multiple-step measurement Up to four measurement steps involving positioners, detectors, and end calculations (e.g., to support dichroism experiments) can be done with the `4step.db` database and the related MEDM display, `4step.adl`. The entire measurement sequence can be involved in a scan by treating the 4step database as you would treat the scaler or mca software.
    - Signal averaging Calculating the average of a series of PV values is supported by the `userAve10.db` database, and `userAve.adl` display. The database can calculate one-shot or running averages, and - for PID loops - can fit to a line, to mitigate the time delay inherent in signal averaging
    - Interpolation EPICS supports breakpoint tables for linear interpolation of a dataset fixed at boot time. The synApps `interp` support (in the __calc__module) can run a drive or readback value through an interpolation table built at run time.
    - Glue electronics The __softGlue__ module supports simple digital electronic circuits that can be built at run time.
4. Running synApps 
    1. Boot parameters See `xxx/iocBoot/ioc*/bootParms` for sample boot parameters.
    2. Display manager 
        - MEDM See the MEDM Operator's Manual for detailed information on the special needs of this X11/Motif program. I'll assume those needs have been met.
            
            MEDM uses a search path list to find .adl files, and we'd like for that path list to refer to the synApps module versions actually in use. To generate the search path list from an application's configure/RELEASE file, edit the file `xxx/start_epics_xxx` so it sets the environment variables `EPICS_APP` and `EPICS_APP_ADL_DIR`. Here's an example:
            
            ```
            setenv EPICS_APP /home/oxygen/MOONEY/epics/synApps/support/xxx
            setenvEPICS_APP_ADL_DIR ${EPICS_APP}/xxxApp/op/adl
            ```

            If you plan to run MEDM on a workstation that isn't on the same subnet as the IOC's, you'll need to uncomment and edit the definition of the environment variable `EPICS_CA_ADDR_LIST`. In principle, you should be able to name only the broadcast address for the subnet that contains the IOC's, but if this doesn't work, you can put in the IP addresses of all the IOC's you want to connect with, separated by spaces, as follows: 
            ```
            setenv EPICS_CA_ADDR_LIST "164.54.53.126 164.54.53.127"
            ```
            
            If you want to use arrays larger than 16000 bytes (e.g., MCA spectra of more than 4000 channels, or scans of more than 2000 data points), you must set the environment variable `EPICS_CA_MAX_ARRAY_BYTES`, in __both__ the IOC and workstation, to the size of the largest array you plan to send over the network, plus the size of the extra data channel access might be asked to include with the array. On a Unix system, for example, you might say
            
            ```
            setenv EPICS_CA_MAX_ARRAY_BYTES 64008
            ```
            
            in the IOC's common.iocsh file, you'd say 
            ```
            epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", 64008)
            ```
            
            This will permit scans of up to 8000 points (8000 doubles \* 8 bytes per double + 8 bytes for channel-access overhead), and mca spectra of up to 16000 channels. To bring up the top-level MEDM display for synApps software, cd to xxx and type "start\_MEDM\_xxx" (e.g., start\_MEDM\_1bma). This script locates the directories that might have MEDM-display files and includes them in the environment variable EPICS\_DISPLAY\_PATH, cd's to xxxApp/op/adl, and runs MEDM with the default top-level display file.
        - caQtDM caQtDM display files (\*.ui) in synApps were translated from MEDM-display files (\*.adl) with the adl2ui translator in caQtDM-3-8-10 (available from http://epics.web.psi.ch/software/caqtdm/). (Actually, the version used to translate .adl files in xxx and other synApps modules was modified from the pristine version, so that related display menu buttons would look as they do in MEDM.)
            
            caQtDM implements a search path list very much as in MEDM, so we can use the same technique to autogenerate that path from an application's configure/RELEASE file. Edit the file `xxx/start_caQtDM_xxx` so it sets the environment variables `EPICS_APP` and `EPICS_APP_UI_DIR`. Here's an example:
            
            ```
            setenv EPICS_APP /home/oxygen/MOONEY/epics/synApps/support/xxx
            setenv EPICS_APP_UI_DIR ${EPICS_APP}/xxxApp/op/ui
            ```
            
            Other environment variables used by caQtDM are the same as for MEDM.
        - CSS-BOY CSS-BOY display files (\*.opi) in synApps were translated from MEDM-display files (\*.adl) using the ADL-to-BOY translator included with CSS-BOY.
            
            CSS-BOY can use a search path list for display files, as MEDM does, but the path is defined differently. One way to set it is to select the menu "Edit/Preferences", then select "CSS Applications/Display/BOY" and type the path into the "OPI Search Path" box. See CSS-BOY documentation for other options.
    3. autosave/restore You must give a vxWorks IOC write permission to xxx/iocBoot/ioc\*/autosave so it can write the files auto\_positions.sav and auto\_settings.sav there. It's also helpful to set the autosave directory's 'group' bit so that files the crate writes will be owned by the owner of the directory instead of by . Normally, I do this: 
        ```
        chmod a+w,g+s autosave
        ```
        
        If you are using autosaveBuild, you must give a vxWorks IOC write permission to the directory where it builds the autosave files. The default IOC builds these files in the autosave directory, so there isn't any need to change further permissions, only if you change common.iocsh to change the build location. Also, you must use a version of vxWorks that can append to files via NFS. vxWorks 6.9.4.1 works.
        
        To modify the list of PV's that are saved and restored, edit the files xxx/iocBoot/ioc\*/auto\_settings.req and xxx/iocBoot/ioc\*/auto\_positions.req
        
        The autosave software is started by the lines "`create_monitor_set(...`" in xxx/iocBoot/ioc\*/st.cmd. The restore happens during iocInit as a result of function calls inserted into initHooks.o, which is included in the library provided by the __autosave__ module, and linked into the executable loaded by xxx/iocBoot/ioc\*/st.cmd.
        
        6\. saveData saveData is a CA client that monitors sscan records and saves scan data to disk. On vxWorks, this is an NFS-mounted disk; on other operating systems, it's whatever file system the system provides for the standard C library. The saveData software is configured with the file xxx/iocBoot/ioc\*/saveData.req, which needs no special attention unless you want to modify the list of EPICS PV's whose values are to be saved with every data file. To do this, look for the string "\[extraPV\]" in the file, and edit the list of PV's immediately following that string. If an entry in this list contains only the PV name, saveData will describe the PV, in the data file, using the .DESC field of the record that contains that PV. If a string follows the PV name, saveData will use the string instead.


How to extend synApps
---------------------


Like all EPICS software, synApps can be extended in many ways, and at many levels, by EPICS developers and users. (That's how the package came to exist in the first place. It started as a single App directory, and folks just added stuff.) But synApps pushes the idea a little bit further toward end users who are not developers. One of the driving notions behind the development of synApps was to put as much of EPICS' flexibility and power as seems both wise and practical into the hands of end users – typically, scientists running experiments – whose backgrounds in software development and implementation vary over a wide range.

Here is a list of techniques by which synApps has already been extended by users and developers, arranged *very* roughly according to the amounts of effort, skill, and EPICS knowledge required.

- scaler end-calculation customization This is certainly too simple to be considered an extension – all you do is type something like "`(A-B)/I`" into a text box – but it's still pretty useful, and it demonstrates a technique that will be used for much more sophisticated purposes.
- scan configuration The first extension that many users attempt is the programming of a scan. This might also seem more like mere *use* than extension, but it can become a very highly evolved skill, and it is software development in a reasonably literal sense. If you buy into the notion that an EPICS database is essentially a program (in a very high-level programming language), then scan configuration can be viewed as the simpler end of a continuum.
- "userCalc" programming synApps facilitates run-time programming of a number of EPICS record types, by providing the following kinds of support:
    
    
    - databases dedicated to this purpose
    - autosave-request files, intended to preserve run-time programming through IOC reboots
    - display files exposing those fields most appropriate for run-time programming
    - display files that contain documentation intended for run-time reference by end users.
    
    The word "userCalc" has become generic for the records and database fragments with which run-time programming is done, and most of the records so used are, in fact, calculation records whose expressions can be modified by users. But synApps also contains records and databases intended for run-time programming of other kinds:
    
    
    - sequences of operations (in __calc__)   
        `userStringSeqs10.db, userStringSeqs10_settings.req, userStringSeq*.adl`
    - feedback loops (in __std__)   
        `*pid_control.db, *pid_control_settings.req, pid*.adl`
    - ramping/tweaking of control parameters (in __std__)   
        `ramp_tweak.db, ramp_tweak_settings.req, ramp_tweak*.adl`
    - impromptu device support for serial and other message based devices (in __ip__)   
        `deviceCmdReply.db, deviceCmdReply_settings.req, deviceCmdReply*.adl`
    - a 1-4 step sequence of *set-conditions/acquire-data/calculate* operations (in __std__)   
        `4step.db, 4step_settings.req, 4step.adl`
    - lookup-table definition and use (in __calc__)   
        `interpNew.db, interpNew_settings.req, interpNew.adl`
    
    In addition to "userCalcs", many synApps records and databases contain sections intended primarily for run-time programming by end users. Examples include end-of-acquisition calculations for scalers and digital multimeters; region-of-interest summing, and background-subtraction for mca records.
- [caputRecorder](https://github.com/epics-modules/caputRecorder/releases) macro recording Users who know how to accomplish a task by executing or modifying EPICS records can write software to automate that task using caputRecorder:
    
    
    1. Enter a macro name to identify the task.
    2. Press caputRecorder's "Start" button.
    3. Perform the task manually.
    4. Press caputRecorder's "Stop" button.
- Display editing End users know better than anybody what they want in a graphical user interface. One thing they've demonstrated that they want is the ability to have some control over the user interface without having to specify every little detail to a programmer. MEDM/caQtDM/CSS-Boy provides end users with the ability easily to create custom displays, and synApps provides over 800 user-interface files that can be copied from, called up from, or included as part of a user crafted display.
- IOC command-file editing An EPICS IOC is populated and configured by ASCII command files, which knowledgeable end users can edit to add motors, change default baud rates, load additional copies of databases, etc.
- Development of client-side scripts Many synApps end users have written scripts, in languages such as the unix shell, Python, SPEC macro, IDL, tcl, perl, and Labview, to simplify and/or standardize beamline operations. Any language can be used for this purpose, if it can be fitted with a Channel-Access interface.
- EPICS-database development One very easy step from run-time programming to EPICS-database development can be taken by using the wxPython program, snapDb.py, (in the *utils*directory) to "freeze" a collection of programmed userCalcs into an independently loadable database. snapDb can also generate a first cut at a user interface for the database.
    
    But most EPICS database development is done with a database-configuration tool, such as VDCT, or with a text editor. In any case, EPICS-database development typically involves the selection of device support, the specification of links and link attributes, and the setting of parameters. More sophisticated development also involves the programming of an initialization strategy into the database, and maybe the writing of an autosave-request file, for it.
- Development of subroutines for the *sub* and *aSub* record types This is probably the simplest way to add custom C code to an EPICS application. SynApps contains several examples of this type of code, among them are arrayTest.c, interp.c, and subAve.c, all in the directory support/calc/calcApp/src.
- Development of State-Notation-Language programs This is probably the next easiest, and the next most capable, way of adding compiled code to an application. SNL also introduces to this list the notion of client-side program development, for an SNL program is a Channel Access client, even though it runs on an IOC. Again, synApps has many examples, which you can find by searching for ".st" and ".stt" files.
    
    Documentation for SNL can be found in the __seq__ module, a copy of which is bundled with synApps.
- Device-support development If synApps doesn't contain device support for the device you want to use, you can probably find (in synApps or elsewhere) a device-support example that has, at least, the structure of the sort of support you will need.
    
    Nobody writes device support from scratch; it's just not an effective way to develop. Everybody tries to find the closest approximation to what they need, and modifies it until it serves their purpose. One important use of the EPICS tech-talk email list is to gather suggestions, from folks further up the learning curve, on what might be a good piece of code to use or modify for a particular purpose.
- Development of client-side GUI programs This requires a lot of skill, effort, and information. Developers at this level need the *EPICS Application Developer's Guide*, the *Channel Access Reference Manual*, and very capable cross-platform GUI infrastructure.
- Module development This also requires a lot of skill, effort, and information. Developers at this level need the *EPICS Application Developer's Guide*, and the *EPICS Record Reference Manual*. One of the very best features of EPICS is the fact that experts in module development can collaborate with experts in client-side development, even if the developers are unaware of each other.

All of the extension strategies described above produce (or, at least *can* produce) results which are *fully* integrated into the control system. This means that they can be used in further extensions by the same techniques. Thus, for example, motors ganged together by a transform record can be scanned, driven by a PID loop, or controlled by another userCalc.



The synApps utils directory
---------------------------


The synApps support/utils directory contains a variety of executables that may be useful in administering and/or using synApps. Some of these tools are probably peculiar to the way synApps is used at APS.

> changePrefix, doSed 
* These are for the application developer's convenience in changing EPICS prefixes in a user directory. You must be in the top level of the user directory to run changePrefix, and you should do a "make clean uninstall" before running it. Example of use:
> ```
>     cd $(SYNAPPS)/ioc/1bm
>     changePrefix xxx 1bma
> ```
 
> copyAdl 
* Look through synApps for .adl files, and copy them all to a specified directory Example of use:
> ``` 
>     copyAdl $SYNAPPS/support adl_files
> ```

> convertIocFiles.py 
* This file, and its associates, are intended to help convert an IOC directory from one version of EPICS to another, by collecting data from an existing IOC directory, and attempting to correctly edit files in a new IOC directory. See support/utils/HowToUse\_convertIocFiles.txt for more information on this program. 
> mdautils-src.tar.gz  
* This tar file contains utility programs for using data files written by the __sscan__ module's "saveData" program. These programs were written by Dohn Arms, and contributed to synApps. 
> mdaExplorer 
* This wxPython program displays the content of MDA files, and directories of MDA files. (An MDA file is the scan-data file produced by the synApps __sscan__ module's saveData software during a scan.) 
> mdaPythonUtils 
* A collection of python programs that read, write, modify, and translate MDA files. 
> snapDb 
* A wxPython rapid development tool for EPICS databases and MEDM display files. This program supports the use of EPICS' run-time programmability to prototype EPICS databases, using records loaded into an IOC. It's particularly useful with synApps "userCalcs", a collection of various record types intended for end users to program at run time.


### Appendix: Device support in or distributed with synApps (including support from EPICS base)

| record | bus-type | codename | DTYP name |
|---|---|---|---|
| aai | CONSTANT | devAaiSoft | Soft Channel |
| aai | INST\_IO | devaaiStream | stream |
| aao | CONSTANT | devAaoSoft | Soft Channel |
| aao | INST\_IO | devaaoStream | stream |
| ai | CONSTANT | devAiSoft | Soft Channel |
| ai | CONSTANT | devAiSoftRaw | Raw Soft Channel |
| ai | INST\_IO | devTimestampAI | Soft Timestamp |
| ai | INST\_IO | devAiGeneralTime | General Time |
| ai | INST\_IO | asynAiInt32 | asynInt32 |
| ai | INST\_IO | asynAiInt32Average | asynInt32Average |
| ai | INST\_IO | asynAiFloat64 | asynFloat64 |
| ai | INST\_IO | asynAiFloat64Average | asynFloat64Average |
| ai | GPIB\_IO | devGpib | GPIB init/report |
| ai | CONSTANT | devAiTodSeconds | Sec Past Epoch |
| ai | INST\_IO | devAiStrParm | asyn ai stringParm |
| ai | INST\_IO | devAiHeidND261 | asyn ai HeidND261 |
| ai | INST\_IO | devAiMKS | HPS SensaVac 937 |
| ai | INST\_IO | devAiMPC | asyn MPC |
| ai | GPIB\_IO | devAiGP307Gpib | Vg307 GPIB Instrument |
| ai | BBGPIB\_IO | devAiAX301 | PZT Bug |
| ai | INST\_IO | devAiTelevac | asyn Televac |
| ai | INST\_IO | devAiTPG261 | asyn TPG261 |
| ai | INST\_IO | devaiStream | stream |
| ai | INST\_IO | devAiStats | IOC stats |
| ai | INST\_IO | devAiClusts | IOC stats clusts |
| ai | GPIB\_IO | devAidg535 | dg535 |
| ai | VME\_IO | devAiVaroc | ESRF Varoc SSI Encoder Iface |
| ai | VME\_IO | devAiBunchClkGen | APS Bunch Clock |
| ai | VME\_IO | devAiA32Vme | Generic A32 VME |
| ai | VME\_IO | devAiAvmeMRD | devAvmeMRD |
| ai | VME\_IO | devIK320Ai | Heidenhain IK320 |
| ai | VME\_IO | devIK320GroupAi | Heidenhain IK320 Group |
| ai | GPIB\_IO | devAiHeidAWE1024 | Heidenhein Encoder |
| ai | GPIB\_IO | devAiKeithleyDMM199 | KeithleyDMM199 |
| ai | INST\_IO | devAiAbDcm | Ab Dcm |
| ai | INST\_IO | devInterfaceAI1 | InterfaceAI1 |
| ai | INST\_IO | devAiAb1791 | Allen Bradley 1791 |
| ai | AB\_IO | devAiAbSlcDcm | AB-SLC500DCM |
| ai | AB\_IO | devAiAbSlcDcmSigned | AB-SLC500DCM-Signed |
| ai | AB\_IO | devAiAb1771Il | AB-1771IL-Analog In |
| ai | AB\_IO | devAiAb1771Ife | AB-1771IFE |
| ai | AB\_IO | devAiAb1771Ixe | AB-1771IXE-Millivolt In |
| ai | AB\_IO | devAiAb1771IfeSe | AB-1771IFE-SE |
| ai | AB\_IO | devAiAb1771IfeMa | AB-1771IFE-4to20MA |
| ai | AB\_IO | devAiAb1771Ife0to5V | AB-1771IFE-0to5Volt |
| ai | AB\_IO | devAiAb1771IrPlatinum | AB-1771RTD-Platinum |
| ai | AB\_IO | devAiAb1771IrCopper | AB-1771RTD-Copper |
| ai | INST\_IO | devAiStats | VX stats |
| ai | INST\_IO | devAiClusts | VX stats clusts |
| ao | CONSTANT | devAoSoft | Soft Channel |
| ao | CONSTANT | devAoSoftRaw | Raw Soft Channel |
| ao | CONSTANT | devAoSoftCallback | Async Soft Channel |
| ao | INST\_IO | asynAoInt32 | asynInt32 |
| ao | INST\_IO | asynAoFloat64 | asynFloat64 |
| ao | INST\_IO | devAoStrParm | asyn ao stringParm |
| ao | INST\_IO | devAoEurotherm | asyn ao Eurotherm |
| ao | INST\_IO | devAoMPC | asyn MPC |
| ao | BBGPIB\_IO | devAoAX301 | PZT Bug |
| ao | INST\_IO | devAoTPG261 | asyn TPG261 |
| ao | INST\_IO | devaoStream | stream |
| ao | INST\_IO | devAoStats | IOC stats |
| ao | GPIB\_IO | devAodg535 | dg535 |
| ao | VME\_IO | devAoBunchClkGen | APS Bunch Clock |
| ao | VME\_IO | devAoA32Vme | Generic A32 VME |
| ao | VME\_IO | devAoVMI4116 | VMIVME-4116 |
| ao | VME\_IO | devAoAvme9210 | AVME-9210 |
| ao | GPIB\_IO | devAoHeidAWE1024 | Heidenhein Encoder |
| ao | GPIB\_IO | devAoKeithleyDMM199 | KeithleyDMM199 |
| ao | INST\_IO | devAoAbDcm | Ab Dcm |
| ao | INST\_IO | devInterfaceAO1 | InterfaceAO1 |
| ao | INST\_IO | devAoAb1791 | Allen Bradley 1791 |
| ao | AB\_IO | devAoAbSlcDcm | AB-SLC500DCM |
| ao | AB\_IO | devAoAb1771Ofe | AB-1771OFE |
| ao | INST\_IO | devAoStats | VX stats |
| bi | CONSTANT | devBiSoft | Soft Channel |
| bi | CONSTANT | devBiSoftRaw | Raw Soft Channel |
| bi | INST\_IO | asynBiInt32 | asynInt32 |
| bi | INST\_IO | asynBiUInt32Digital | asynUInt32Digital |
| bi | INST\_IO | devBiStrParm | asyn bi stringParm |
| bi | INST\_IO | devBiMPC | asyn MPC |
| bi | GPIB\_IO | devBiGP307Gpib | Vg307 GPIB Instrument |
| bi | INST\_IO | devBiTelevac | asyn Televac |
| bi | INST\_IO | devBiTPG261 | asyn TPG261 |
| bi | INST\_IO | devbiStream | stream |
| bi | GPIB\_IO | devBidg535 | dg535 |
| bi | VME\_IO | devBiHP10895LaserAxis | HP interferometer |
| bi | VME\_IO | devBiBunchClkGen | APS Bunch Clock |
| bi | VME\_IO | devBiA32Vme | Generic A32 VME |
| bi | VME\_IO | devBiAvmeMRD | devAvmeMRD |
| bi | VME\_IO | devBiAvme9440 | AVME9440 I |
| bi | GPIB\_IO | devBiHeidAWE1024 | Heidenhein Encoder |
| bi | GPIB\_IO | devBiKeithleyDMM199 | KeithleyDMM199 |
| bi | AB\_IO | devBiAb | AB-Binary Input |
| bi | AB\_IO | devBiAb16 | AB-16 bit BI |
| bi | AB\_IO | devBiAb32 | AB-32 bit BI |
| bi | INST\_IO | devBiAbDcm | Ab Dcm |
| bo | CONSTANT | devBoSoft | Soft Channel |
| bo | CONSTANT | devBoSoftRaw | Raw Soft Channel |
| bo | CONSTANT | devBoSoftCallback | Async Soft Channel |
| bo | INST\_IO | devBoGeneralTime | General Time |
| bo | INST\_IO | asynBoInt32 | asynInt32 |
| bo | INST\_IO | asynBoUInt32Digital | asynUInt32Digital |
| bo | INST\_IO | devBoStrParm | asyn bo stringParm |
| bo | INST\_IO | devBoMPC | asyn MPC |
| bo | GPIB\_IO | devBoGP307Gpib | Vg307 GPIB Instrument |
| bo | BBGPIB\_IO | devBoAX301 | PZT Bug |
| bo | INST\_IO | devBoTPG261 | asyn TPG261 |
| bo | INST\_IO | devboStream | stream |
| bo | GPIB\_IO | devBodg535 | dg535 |
| bo | VME\_IO | devBoHP10895LaserAxis | HP interferometer |
| bo | VME\_IO | devBoBunchClkGen | APS Bunch Clock |
| bo | VME\_IO | devBoA32Vme | Generic A32 VME |
| bo | VME\_IO | devBoAvmeMRD | devAvmeMRD |
| bo | VME\_IO | devBoAvme9440 | AVME9440 O |
| bo | GPIB\_IO | devBoHeidAWE1024 | Heidenhein Encoder |
| bo | GPIB\_IO | devBoKeithleyDMM199 | KeithleyDMM199 |
| bo | AB\_IO | devBoAb | AB-Binary Output |
| bo | AB\_IO | devBoAb16 | AB-16 bit BO |
| bo | AB\_IO | devBoAb32 | AB-32 bit BO |
| bo | INST\_IO | devBoAbDcm | Ab Dcm |
| bo | INST\_IO | softGlueShow | softGlueShow |
| calcout | CONSTANT | devCalcoutSoft | Soft Channel |
| calcout | CONSTANT | devCalcoutSoftCallback | Async Soft Channel |
| calcout | INST\_IO | devcalcoutStream | stream |
| event | CONSTANT | devEventSoft | Soft Channel |
| longin | CONSTANT | devLiSoft | Soft Channel |
| longin | INST\_IO | devLiGeneralTime | General Time |
| longin | INST\_IO | asynLiInt32 | asynInt32 |
| longin | INST\_IO | asynLiUInt32Digital | asynUInt32Digital |
| longin | INST\_IO | devLiStrParm | asyn li stringParm |
| longin | INST\_IO | devlonginStream | stream |
| longin | GPIB\_IO | devLidg535 | dg535 |
| longin | VME\_IO | devLiHP10895LaserAxis | HP interferometer |
| longin | VME\_IO | devLiA32Vme | Generic A32 VME |
| longin | VME\_IO | devLiAvmeMRD | devAvmeMRD |
| longin | GPIB\_IO | devLiHeidAWE1024 | Heidenhein Encoder |
| longin | GPIB\_IO | devLiKeithleyDMM199 | KeithleyDMM199 |
| longin | INST\_IO | devLiAbDcm | Ab Dcm |
| longin | AB\_IO | devLiAbSlcDcm | AB-SLC500DCM |
| longout | CONSTANT | devLoSoft | Soft Channel |
| longout | CONSTANT | devLoSoftCallback | Async Soft Channel |
| longout | INST\_IO | asynLoInt32 | asynInt32 |
| longout | INST\_IO | asynLoUInt32Digital | asynUInt32Digital |
| longout | INST\_IO | devLoStrParm | asyn lo stringParm |
| longout | BBGPIB\_IO | devLoAX301 | PZT Bug |
| longout | INST\_IO | devlongoutStream | stream |
| longout | GPIB\_IO | devLodg535 | dg535 |
| longout | VME\_IO | devLoHP10895LaserAxis | HP interferometer |
| longout | VME\_IO | devLoA32Vme | Generic A32 VME |
| longout | GPIB\_IO | devLoHeidAWE1024 | Heidenhein Encoder |
| longout | GPIB\_IO | devLoKeithleyDMM199 | KeithleyDMM199 |
| longout | INST\_IO | devLoAbDcm | Ab Dcm |
| longout | AB\_IO | devLoAbSlcDcm | AB-SLC500DCM |
| longout | INST\_IO | softGlueSigNum | softGlueSigNum |
| mbbi | CONSTANT | devMbbiSoft | Soft Channel |
| mbbi | CONSTANT | devMbbiSoftRaw | Raw Soft Channel |
| mbbi | INST\_IO | asynMbbiInt32 | asynInt32 |
| mbbi | INST\_IO | asynMbbiUInt32Digital | asynUInt32Digital |
| mbbi | INST\_IO | devMbbiTPG261 | asyn TPG261 |
| mbbi | INST\_IO | devmbbiStream | stream |
| mbbi | GPIB\_IO | devMbbidg535 | dg535 |
| mbbi | VME\_IO | devMbbiHP10895LaserAxis | HP interferometer |
| mbbi | VME\_IO | devMbbiA32Vme | Generic A32 VME |
| mbbi | VME\_IO | devMbbiAvmeMRD | devAvmeMRD |
| mbbi | VME\_IO | devMbbiAvme9440 | AVME9440 I |
| mbbi | GPIB\_IO | devMbbiHeidAWE1024 | Heidenhein Encoder |
| mbbi | GPIB\_IO | devMbbiKeithleyDMM199 | KeithleyDMM199 |
| mbbi | AB\_IO | devMbbiAb | AB-Binary Input |
| mbbi | AB\_IO | devMbbiAb16 | AB-16 bit BI |
| mbbi | AB\_IO | devMbbiAb32 | AB-32 bit BI |
| mbbi | AB\_IO | devMbbiAbAdapterStat | AB-Adapter Status |
| mbbi | AB\_IO | devMbbiAbCardStat | AB-Card Status |
| mbbi | INST\_IO | devMbbiAbDcm | Ab Dcm |
| mbbiDirect | CONSTANT | devMbbiDirectSoft | Soft Channel |
| mbbiDirect | CONSTANT | devMbbiDirectSoftRaw | Raw Soft Channel |
| mbbiDirect | INST\_IO | asynMbbiDirectUInt32Digital | asynUInt32Digital |
| mbbiDirect | INST\_IO | devmbbiDirectStream | stream |
| mbbiDirect | AB\_IO | devMbbiDirectAb | AB-Binary Input |
| mbbiDirect | AB\_IO | devMbbiDirectAb16 | AB-16 bit BI |
| mbbiDirect | AB\_IO | devMbbiDirectAb32 | AB-32 bit BI |
| mbbo | CONSTANT | devMbboSoft | Soft Channel |
| mbbo | CONSTANT | devMbboSoftRaw | Raw Soft Channel |
| mbbo | CONSTANT | devMbboSoftCallback | Async Soft Channel |
| mbbo | INST\_IO | asynMbboInt32 | asynInt32 |
| mbbo | INST\_IO | asynMbboUInt32Digital | asynUInt32Digital |
| mbbo | INST\_IO | devMbboMPC | asyn MPC |
| mbbo | INST\_IO | devMbboTPG261 | asyn TPG261 |
| mbbo | INST\_IO | devmbboStream | stream |
| mbbo | GPIB\_IO | devMbbodg535 | dg535 |
| mbbo | VME\_IO | devMbboHP10895LaserAxis | HP interferometer |
| mbbo | VME\_IO | devMbboA32Vme | Generic A32 VME |
| mbbo | VME\_IO | devIK320Funct | Heidenhain IK320 Command |
| mbbo | VME\_IO | devIK320Dir | Heidenhain IK320 Sign |
| mbbo | VME\_IO | devIK320ModeX3 | Heidenhain IK320 X3 Mode |
| mbbo | VME\_IO | devMbboAvme9440 | AVME9440 O |
| mbbo | GPIB\_IO | devMbboHeidAWE1024 | Heidenhein Encoder |
| mbbo | GPIB\_IO | devMbboKeithleyDMM199 | KeithleyDMM199 |
| mbbo | AB\_IO | devMbboAb | AB-Binary Output |
| mbbo | AB\_IO | devMbboAb16 | AB-16 bit BO |
| mbbo | AB\_IO | devMbboAb32 | AB-32 bit BO |
| mbbo | INST\_IO | devMbboAbDcm | Ab Dcm |
| mbboDirect | CONSTANT | devMbboDirectSoft | Soft Channel |
| mbboDirect | CONSTANT | devMbboDirectSoftRaw | Raw Soft Channel |
| mbboDirect | CONSTANT | devMbboDirectSoftCallback | Async Soft Channel |
| mbboDirect | INST\_IO | asynMbboDirectUInt32Digital | asynUInt32Digital |
| mbboDirect | INST\_IO | devmbboDirectStream | stream |
| mbboDirect | AB\_IO | devMbboDirectAb | AB-Binary Output |
| mbboDirect | AB\_IO | devMbboDirectAb16 | AB-16 bit BO |
| mbboDirect | AB\_IO | devMbboDirectAb32 | AB-32 bit BO |
| stringin | CONSTANT | devSiSoft | Soft Channel |
| stringin | INST\_IO | devTimestampSI | Soft Timestamp |
| stringin | INST\_IO | devSiGeneralTime | General Time |
| stringin | INST\_IO | asynSiOctetCmdResponse | asynOctetCmdResponse |
| stringin | INST\_IO | asynSiOctetWriteRead | asynOctetWriteRead |
| stringin | INST\_IO | asynSiOctetRead | asynOctetRead |
| stringin | CONSTANT | devSiTodString | Time of Day |
| stringin | INST\_IO | devSiStrParm | asyn si stringParm |
| stringin | INST\_IO | devSiMPC | asyn MPC |
| stringin | GPIB\_IO | devSiGP307Gpib | Vg307 GPIB Instrument |
| stringin | INST\_IO | devSiTPG261 | asyn TPG261 |
| stringin | INST\_IO | devstringinStream | stream |
| stringin | INST\_IO | devStringinStats | IOC stats |
| stringin | INST\_IO | devStringinEnvVar | IOC env var |
| stringin | INST\_IO | devStringinEpics | IOC epics var |
| stringin | GPIB\_IO | devSidg535 | dg535 |
| stringin | GPIB\_IO | devSiHeidAWE1024 | Heidenhein Encoder |
| stringin | GPIB\_IO | devSiKeithleyDMM199 | KeithleyDMM199 |
| stringin | INST\_IO | devStringinStats | VX stats |
| stringout | CONSTANT | devSoSoft | Soft Channel |
| stringout | CONSTANT | devSoSoftCallback | Async Soft Channel |
| stringout | INST\_IO | devSoStdio | stdio |
| stringout | INST\_IO | asynSoOctetWrite | asynOctetWrite |
| stringout | INST\_IO | devSoStrParm | asyn so stringParm |
| stringout | INST\_IO | devSoEurotherm | asyn so Eurotherm |
| stringout | INST\_IO | devSoMPC | asyn MPC |
| stringout | INST\_IO | devstringoutStream | stream |
| stringout | GPIB\_IO | devSodg535 | dg535 |
| stringout | VME\_IO | devIK320Parm | Heidenhain IK320 Parameter |
| stringout | GPIB\_IO | devSoHeidAWE1024 | Heidenhein Encoder |
| stringout | GPIB\_IO | devSoKeithleyDMM199 | KeithleyDMM199 |
| stringout | INST\_IO | asynSoftGlue | softGlue |
| subArray | CONSTANT | devSASoft | Soft Channel |
| waveform | CONSTANT | devWfSoft | Soft Channel |
| waveform | INST\_IO | asynWfOctetCmdResponse | asynOctetCmdResponse |
| waveform | INST\_IO | asynWfOctetWriteRead | asynOctetWriteRead |
| waveform | INST\_IO | asynWfOctetRead | asynOctetRead |
| waveform | INST\_IO | asynWfOctetWrite | asynOctetWrite |
| waveform | INST\_IO | asynInt8ArrayWfIn | asynInt8ArrayIn |
| waveform | INST\_IO | asynInt8ArrayWfOut | asynInt8ArrayOut |
| waveform | INST\_IO | asynInt16ArrayWfIn | asynInt16ArrayIn |
| waveform | INST\_IO | asynInt16ArrayWfOut | asynInt16ArrayOut |
| waveform | INST\_IO | asynInt32ArrayWfIn | asynInt32ArrayIn |
| waveform | INST\_IO | asynInt32ArrayWfOut | asynInt32ArrayOut |
| waveform | INST\_IO | asynInt32TimeSeries | asynInt32TimeSeries |
| waveform | INST\_IO | asynFloat32ArrayWfIn | asynFloat32ArrayIn |
| waveform | INST\_IO | asynFloat32ArrayWfOut | asynFloat32ArrayOut |
| waveform | INST\_IO | asynFloat64ArrayWfIn | asynFloat64ArrayIn |
| waveform | INST\_IO | asynFloat64ArrayWfOut | asynFloat64ArrayOut |
| waveform | INST\_IO | asynFloat64TimeSeries | asynFloat64TimeSeries |
| waveform | INST\_IO | devwaveformStream | stream |
| waveform | INST\_IO | devWaveformStats | IOC stats |
| waveform | VME\_IO | devWfBunchClkGen | APS Bunch Clock |
| asyn | INST\_IO | asynRecordDevice | asynRecordDevice |
| scaler | INST\_IO | devScalerAsyn | Asyn Scaler |
| scaler | VME\_IO | devScaler | Joerger VSC8/16 |
| scaler | VME\_IO | devScaler\_VS | Joerger VS |
| scaler | VME\_IO | devScalerCamac | CAMAC scaler |
| epid | CONSTANT | devEpidSoft | Soft Channel |
| epid | CONSTANT | devEpidSoftCB | Async Soft Channel |
| epid | INST\_IO | devEpidFast | Fast Epid |
| scalcout | CONSTANT | devsCalcoutSoft | Soft Channel |
| scalcout | INST\_IO | devscalcoutStream | stream |
| acalcout | CONSTANT | devaCalcoutSoft | Soft Channel |
| swait | CONSTANT | devSWaitIoEvent | Soft Channel |
| busy | CONSTANT | devBusySoft | Soft Channel |
| busy | CONSTANT | devBusySoftRaw | Raw Soft Channel |
| busy | INST\_IO | asynBusyInt32 | asynInt32 |
| mca | CONSTANT | devMCA\_soft | Soft Channel |
| mca | INST\_IO | devMcaAsyn | asynMCA |
| motor | INST\_IO | devMotorAsyn | asynMotor |
| motor | VME\_IO | devMCB4B | ACS MCB-4B |
| motor | VME\_IO | devSoloist | Soloist |
| motor | VME\_IO | devMCDC2805 | MCDC2805 |
| motor | VME\_IO | devIM483SM | IM483SM |
| motor | VME\_IO | devIM483PL | IM483PL |
| motor | VME\_IO | devMDrive | MDrive |
| motor | VME\_IO | devSC800 | SC-800 |
| motor | VME\_IO | devPM304 | Mclennan PM304 |
| motor | VME\_IO | devMicos | Micos MoCo |
| motor | VME\_IO | devMVP2001 | MVP2001 |
| motor | VME\_IO | devPMNC87xx | PMNC87xx |
| motor | VME\_IO | devMM3000 | MM3000 |
| motor | VME\_IO | devMM4000 | MM4000 |
| motor | VME\_IO | devPM500 | PM500 |
| motor | VME\_IO | devESP300 | ESP300 |
| motor | VME\_IO | devEMC18011 | EMC18011 |
| motor | VME\_IO | devPC6K | PC6K |
| motor | VME\_IO | devPIJEDS | PIJEDS |
| motor | VME\_IO | devPIC844 | PIC844 |
| motor | VME\_IO | devPIC630 | PI C630 |
| motor | VME\_IO | devPIC848 | PIC848 |
| motor | VME\_IO | devPIC662 | PIC662 |
| motor | VME\_IO | devPIC862 | PIC862 |
| motor | VME\_IO | devPIC663 | PIC663 |
| motor | VME\_IO | devPIE710 | PIE710 |
| motor | VME\_IO | devPIE516 | PIE516 |
| motor | VME\_IO | devPIE816 | PIE816 |
| motor | VME\_IO | devSPiiPlus | SPiiPlus |
| motor | VME\_IO | devSmartMotor | SmartMotor |
| motor | CONSTANT | devMotorSoft | Soft Channel |
| motor | VME\_IO | devMDT695 | MDT695 |
| motor | VME\_IO | devMotorSim | Motor Simulation |
| motor | VME\_IO | devE500 | E500 |
| motor | VME\_IO | devPmac | PMAC |
| motor | VME\_IO | devOMS | OMS VME8/44 |
| motor | VME\_IO | devOms58 | OMS VME58 |
| motor | VME\_IO | devMAXv | OMS MAXv |
| motor | VME\_IO | devOmsPC68 | OMS PC68/78 |
| digitel | INST\_IO | devDigitelPump | asyn DigitelPump |
| vs | INST\_IO | devVacSen | asyn VacSen |

- - - - - -

 Suggestions and Comments to:   
 [Keenan Lang](mailto:klang@anl.gov): (klang@anl.gov) or   
 [Tim Mooney ](mailto:mooney@aps.anl.gov): (mooney@aps.anl.gov)   
 Beamline Controls &amp; Data Acquisition Group  
 Advanced Photon Source, Argonne National Laboratory
