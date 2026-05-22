---
layout: default
title: Overview
nav_order: 2
---


synApps 6.4
===========

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
> a linked library, in calc/lib/&lt;arch&gt;
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
> 2. The [EPICS Application Developer's Guide](https://epics.anl.gov/base/R7-0/8-docs/AppDevGuide/AppDevGuide-1.html) is an essential reference for anyone planning to develop or deploy EPICS software. While you won't need to read the guide to build or run synApps, you will need it to understand what you've done, to diagnose problems, and to extend synApps in any significant way.


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
| *docs* | Documentation |
| __dxp__ | Support for X-Ray Instrumentation Associates's DXP digital signal processor |
| __dxpSITORO__ | Support for XIA SITORO based FalconX spectrometers |
| __ether_ip__ | Support for communication with Allen Bradley PLCs via EtherNet/IP |
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
| __scaler__ | Support for scaler bank hardware. |
| __softGlue__ | Support for user-programmed "wiring" of custom FPGA content loaded into an Acromag IP-EP201 module. |
| __softGlueZynq__ | Support for user-programmed "wiring" of custom FPGA content loaded into a Xilinx Zynq board. |
| __sscan__ | Support for scans (programmed control and data acquisition). |
| __std__ | Miscellaneous EPICS support, including the epid (extended PID), sseq (string sequence), and timestamp records; and pvHistory support. |
| __stream__ | Dirk Zimoch's StreamDevice for byte-stream based device communication (serial, TCP/IP, GPIB). |
| *utils* | Miscellaneous tools, including support for converting an application from one version of synApps to another; support for the MDA file format, written by the __sscan__ module; and support for EPICS-application prototyping. |
| __vac__ | Support for vacuum controllers |
| __vme__ | Support for VME hardware |
| __xspress3__ | Support for Quantum Detectors Xpress3 Hardware |
| __xxx__ | Sample user-application directory |
| __Yokogawa\_DAS__ | Support for the Yokogawa MW100 Digital Acquisition Unit. |

See [the assemble_synApps configuration](https://github.com/EPICS-synApps/assemble_synApps) for a complete set of compatible module versions. This release of synApps is compatible with EPICS base 3.15 and 7.0, and the following EPICS modules, which are produced and maintained by other members of the EPICS collaboration. These modules are not part of synApps, but their maintainers have permitted us to distribute copies along with synApps:

| Module | description |
|---|---|
| __allenBradley__ | for communicating with Allen Bradley PLC's (ANL) |
| __ipac__ | required for IndustryPack support (ANL) |
| __asyn__ | required by many modules (ANL) |
| __seq__ | for SNL programs in synApps   source: https://github.com/epics-modules/sequencer |
| __stream__ | configurable device support for message-based devices (PSI)   source: https://github.com/paulscherrerinstitute/StreamDevice |
| __devIocStats__ | IOC statistics, replaces vxStats (SLAC)   source: https://github.com/epics-modules/iocStats |

> Previous versions of synApps included and relied on the __genSub__, __ccd__, and __pilatus__ modules. Beginning with EPICS 3.14.10, a replacement for the genSub record, called the aSub record, is included in base, and synApps has been modified to use it instead of the genSub record. The __ccd__ and __pilatus__ modules have been replaced by the __areaDetector__ module.

For convenience, this distribution includes the modules listed above, in place and ready to build, with minor modifications to build files. A few of the modules have suffered more substantial modifications to fix problems, add display files, etc.

synApps includes software developed by the Beamline Controls &amp; Data Acquisition, Software Services, and Accelerator Controls groups of the Advanced Photon Source (APS); by developers in APS Collaborative Access Teams – notably, Mark Rivers (CARS-CAT); and by developers in the EPICS collaboration outside of the APS – notably, those at the Diamond Light Source, the Berliner Elektronenspeicherring-Gesellschaft für Synchrotronstrahlung (BESSY), the Stanford Linear Accelerator Center (SLAC), the Swiss Light Source (SLS)/Paul Scherrer Institut (PSI), the National Synchrotron Light Source (NSLS), the Deutsches Elektronen Synchrotron (DESY), the Spallation Neutron Source (SNS), the Australian Light Source, and the Canadian Light Source.

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

synApps is normally deployed as a two-part system: a 'support' directory, and one or more 'user' directories. The support directory can be installed on a read-only file system, along with EPICS base and other modules, and used from there by user directories. Each user directory typically begins as a copy of the __xxx__ module, customized and extended to suit a particular application and set of hardware.

There are two ways to obtain the synApps support directory:

#### Option 1: Download a prebuilt tarball

Download a release tarball from the [synApps releases page](https://github.com/EPICS-synApps/support/releases). This provides a pre-assembled support directory with all modules at tested, compatible versions.

#### Option 2: Use the assemble_synApps script

The [assemble_synApps](https://github.com/EPICS-synApps/assemble_synApps) perl script will clone all synApps modules from GitHub at compatible versions and configure them to build together. This is the recommended approach for users who want to customize which modules are included or track specific module versions.

The script can be configured to select module versions, enable or disable specific modules, and set the path to EPICS base. See the [assemble_synApps documentation](https://github.com/EPICS-synApps/assemble_synApps) for details.

#### The support directory

Once deployed by either method, the support directory will contain:

```
synApps/support/
    Makefile
    configure/
        CONFIG
        CONFIG_SITE
        RELEASE                         <-- EDIT SUPPORT and EPICS_BASE paths
        ...
    alive/
    areaDetector/
    asyn/
    autosave/
    busy/
    calc/
    camac/
    caputRecorder/
    dac128V/
    delaygen/
    devIocStats/
    docs/
    dxp/
    ether_ip/
    ip/
    ip330/
    ipac/
    ipUnidig/
    labjack/
    love/
    lua/
    mca/
    measComp/
    modbus/
    motor/
    optics/
    quadEM/
    scaler/
    seq/
    softGlue/
    sscan/
    std/
    StreamDevice/
    utils/
    vac/
    vme/
    xxx/
```

#### The user directory

A user directory is typically constructed from the __xxx__ module, which serves as a template. At its simplest, a single copy of __xxx__ supports a single IOC. If several IOCs cooperate to serve a single application (such as a synchrotron beamline), one might make several independent copies of __xxx__, or extend a single copy to contain multiple xxxApp directories and multiple iocBoot/iocxxx directories.

To create a user directory from the __xxx__ template, copy the __xxx__ module directory, then run `changePrefix` to rename all PV prefixes:

```
    cp -r $(SYNAPPS)/support/xxx /path/to/ioc/1bm
    cd /path/to/ioc/1bm
    $(SYNAPPS)/support/utils/changePrefix xxx 1bma
```

Then edit the following files to configure the user directory:

> `1bm/configure/RELEASE`
* Edit the definition of `SUPPORT` with the correct path to the support directory.
> `1bm/iocBoot/ioc1bma/*.cmd`, `1bm/iocBoot/ioc1bma/*.iocsh`
* Configure hardware, load databases, and set IOC parameters.
> `1bm/setup_epics_common`
* Set the value of Channel Access environment variables.
> `1bm/start_caQtDM_1bma` or `1bm/start_phoebus_1bma`
* Edit to specify the path to the application and display-file directories.

The association between a user directory and the support directory on which it depends is made entirely by the file `configure/RELEASE` in the user directory.

> *Note that the modules in synApps are interdependent. Many of the modules depend on the __asyn__ module, for example, and there are many other dependencies, both direct and implied. The complete set of modules selected by a user directory must be self consistent, and the EPICS build will ensure this, unless you tell it not to, by defining `CHECK_RELEASE=NO` or `CHECK_RELEASE=WARN` in `configure/CONFIG_SITE`.*

The synApps build imposes an additional constraint on module names. Because synApps uses EPICS build rules to descend from `support` into the modules, module names may not include the character '.'. (The EPICS build rules expect '.' to be followed by a host or target architecture.) <a name="How to build synApps"></a>



How to build synApps
--------------------


1. **System configuration.** Before building synApps, you should ensure that your system has the tools, libraries, header files, etc. required to build the modules you want to build. Key dependencies include:

    - A built copy of EPICS base 3.15 or 7.0.
    - A C/C++ compiler (gcc/g++ on Linux, MSVC on Windows).
    - GNU Make (the same version used to build EPICS base).
    - Perl (required by the EPICS build system).
    - Linux: libusb development files if building the __dxp__ module.
    - See the [Cygwin Notes](Cygwin_setup.html) page for Cygwin-specific requirements.

2. **Building the support directory.** If you have deployed synApps using assemble_synApps or a release tarball, building is straightforward:

    1. Edit `support/configure/RELEASE` to set the correct paths for `SUPPORT` and `EPICS_BASE`. Comment out any modules you don't want to build.
    2. If building for multiple host architectures from a single directory, create `EPICS_BASE.<arch>` and/or `SUPPORT.<arch>` files in `support/configure/` to override paths per architecture.
    3. Set the environment variable `EPICS_HOST_ARCH` to the architecture on which you are building (e.g., `linux-x86_64`, `windows-x64`).
    4. In the support directory, run '`make release`'. This propagates the paths from `support/configure/RELEASE` into each module's `configure/RELEASE` file.
    5. In the support directory, run '`make`'. (You can use '`make -j`' to build in parallel.)

    You may need `$(EPICS_BASE)/bin/<arch>` in your `PATH` and `$(EPICS_BASE)/lib/<arch>` in `LD_LIBRARY_PATH`.

    If the build fails because of missing system dependencies, you can disable individual modules by commenting them out of `support/configure/RELEASE` and re-running `make release`.

3. **Building a user directory.** Once the support directory has built, the __xxx__ module will have been configured and built. Copy it, run `changePrefix`, edit the configuration files as described in [How to deploy synApps](<#How to deploy synApps>), and run `make`.



How to make synApps work
------------------------



1. Setting up the IOC

    **Linux soft IOC (typical deployment):**

    Most synApps IOCs are deployed as Linux soft IOCs. The __xxx__ module includes a `softioc/` directory with scripts for running the IOC under `procServ` or `screen`. To start the IOC:

    ```
    cd xxx/iocBoot/iocxxx
    ../../bin/linux-x86_64/xxx st.cmd.Linux
    ```

    The `softioc/` directory provides additional scripts for managing the IOC as a service. Ensure that `caRepeater` is running on the host (it is started automatically by most Channel Access clients).

    **vxWorks IOC:**

    For vxWorks-based VME IOCs, see [vxWorks Configuration](vxWorks.html) for boot parameter setup, serial console configuration, and NFS file system requirements.

2. Display files

    synApps includes display files in several formats: `.ui` files for caQtDM, `.bob` files for Phoebus, `.adl` files for MEDM, and `.opi` files for CSS-BOY. The caQtDM `.ui` files are the primary, actively tested display files. Phoebus `.bob` files are also well-supported. The MEDM `.adl` files are the original display files from which the others were translated, but MEDM itself is now a legacy tool.
3. Fitting synApps to an application This happens in the user directory. Generally, you must tell the IOC what hardware it will control and how to communicate with it. You must specify which motors any slit, table, monochromator, etc., control software is to use. If you use serial or GPIB, you must match port names to hardware devices, set serial-port parameters, and specify GPIB addresses.
    
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
        
        If you want the new motors to work with the 'AllStop' button (`xxx:allstop.VAL`-- see the top-level display `xxx.ui`), load the database `$(MOTOR)/db/motorUtil.db`, and run the command `motorUtilInit("xxx:")`.
        
        If you want the IOC automatically to save positions and settings of the new motors, and restore them when the crate reboots, add lines to the files `xxx/iocBoot/ioc*/auto_settings.req` and `xxx/iocBoot/ioc*/auto_positions.req`.
    - Slits To use a pair of motors to control a slit, search for `2slit.db`in `xxx/iocBoot/ioc*/examples/optics.iocsh`, and edit the `dbLoadRecords()` command you'll find there. The example in `optics.iocsh` loads two copies of `2slit.db` intended for use as the horizontal and vertical members of a four-jaw slit. The display files `2slit*` and `4slit*` are involved in these applications.
        
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
    - Optical tables Optical tables are controlled by a custom EPICS record (the "table" record), used in the database `table.db` and controlled via display files `table*.ui` (caQtDM) or `table*.adl` (MEDM).
        
        Table virtual motors behave in much the same way as do slit virtual motors. However, the table software does not use user/dial offsets in the underlying motor to implement recalibration (it can't, since it works through a nonlinear transform). Instead, the table maintains its own offsets for all of the six coordinated motions it implements. Pressing the "Set" button causes new table positions to modify the offsets instead of moving the table (which is exactly the way motor and slit calibration works). In addition to a "Sync" button, which reads motor positions and calculates the table positions from them, the table display has an "Init" button, which zeros all offsets before doing a "sync" operation. It also has a "Zero" button, which manipulates all the table offsets to make the current table positions zero without moving or recalibrating any motors.
    - Monochromators Several varieties of crystal monochromators are supported in synApps: two constant-offset "channel-cut" monochromators, two varieties of a high-resolution four-crystal monochromator, a spherical-grating monochromator, and a multilayer monochromator. Most are supported by databases paired with State Notation Language (SNL) programs, and display files. The EPICS databases `kohzuSeq.db`, SNL program `kohzuCtl.st`, and displays `kohzu*` are involved in control of two varieties of high-heat-load monochromators. The EPICS database `hrSeq.db`, SNL program `hrCtl.st`, and displays `hSeq*` are involved in control of the high-resolution double-crystal monochromator. The spherical grating monochromator is supported by the database `SGM.db` and the displays `SGM*`. The multilayer monochromator is supported by the database `ml_monoSeq.db` and displays `ml_mono*`.
    - Filters The APS standard user filters combine several motors and solenoids to control the placement of filter material in the beam path. The databases `filterMotor.db` and `filterLock.db`, and the display files `*filter*` are involved in this application.
        
        synApps also supports the XIA filter/shutter box, with two independently developed solutions:
        
        
        - pf4:   
            pf4\*.db  
            pf4\*.adl
        - filterbox:  
            filterBladeNoSensor.db, filterDrive.db  
            filter\_\*\_\*.adl, filterbox\_\*.adl filter\_drive\*.adl
    - Basic run-time programming Impromptu coordinated motions and other bits of run-time programming are handled by what we call a "userCalc" (actually just a swait record with a nice display-file interface) or a "userTransform" (actually just a transform record with a nice display-file interface). We normally load sets of these and other records into each EPICS processor, specifically for end-user programming. Users type in expressions to be evaluated, and link inputs and outputs, as needed, to glue existing objects together to do what they want done at the moment. Here are some examples of the tasks that have been accomplished with userCalcs and userTransforms:
        
        
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
    1. Display manager
        - **caQtDM** (primary) -- caQtDM is the primary display manager for synApps. Display files use the `.ui` format and are located in each module's `op/ui/` directory. All synApps display files are operationally tested in caQtDM.

            To start the caQtDM interface, edit and run the `start_caQtDM_xxx` script in your user directory. This script sets the environment variables `EPICS_APP` and `EPICS_APP_UI_DIR` and generates the display file search path from the application's `configure/RELEASE` file. For example:

            ```
            export EPICS_APP=/path/to/your/ioc
            export EPICS_APP_UI_DIR=${EPICS_APP}/xxxApp/op/ui
            ```

        - **Phoebus** -- Phoebus `.bob` display files are also provided and well-supported. To start Phoebus with synApps displays, edit and run the `start_phoebus_xxx` script in your user directory.

        - **MEDM** (legacy) -- The original MEDM `.adl` display files are still included and can be used with the `start_MEDM_xxx` script, but MEDM is no longer actively developed or the focus of testing.

        If you are running a display manager on a workstation that isn't on the same subnet as the IOCs, you may need to set the environment variable `EPICS_CA_ADDR_LIST` to the IP addresses or broadcast addresses of the subnets containing the IOCs. With EPICS base 7.0 and PV Access, many of the old Channel Access array size limitations (`EPICS_CA_MAX_ARRAY_BYTES`) are no longer relevant when using PVA clients.

    2. autosave/restore

        The autosave directory (`xxx/iocBoot/ioc*/autosave/`) must be writable by the IOC process so it can write the files `auto_positions.sav` and `auto_settings.sav`. On Linux, ensure the IOC user has write permission:

        ```
        chmod a+w,g+s autosave
        ```

        To modify the list of PVs that are saved and restored, edit `xxx/iocBoot/ioc*/auto_settings.req` and `xxx/iocBoot/ioc*/auto_positions.req`. Alternatively, you can use [autosaveBuild](https://epics-modules.github.io/autosave/) to have these files constructed automatically during the boot process.

        The autosave software is started by the `create_monitor_set(...)` calls in `xxx/iocBoot/ioc*/st.cmd`. Restore happens during `iocInit` via initHooks in the __autosave__ module.

    3. saveData

        saveData is a Channel Access client that monitors sscan records and saves scan data to disk. It is configured with the file `xxx/iocBoot/ioc*/saveData.req`, which specifies which sscan records to monitor and which PV values to include in all data files. Look for the `[extraPV]` section in `saveData.req` to customize the list of PVs saved with every data file.


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
- Display editing End users know better than anybody what they want in a graphical user interface. One thing they've demonstrated that they want is the ability to have some control over the user interface without having to specify every little detail to a programmer. caQtDM and Phoebus provide end users with the ability to create custom displays, and synApps provides over 800 user-interface files that can be copied from, called up from, or included as part of a user-crafted display.
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


The synApps support/utils directory contains a variety of scripts and programs that may be useful in administering and/or using synApps.

> changePrefix
* A perl script for changing EPICS PV-name prefixes in a user directory (e.g., when creating a new IOC from the __xxx__ template). You must be in the top level of the user directory to run it. Example of use:
> ```
>     cd /path/to/ioc/1bm
>     $(SYNAPPS)/support/utils/changePrefix xxx 1bma
> ```

> copyScreens.pl
* Search all synApps modules for display files and copy them to a single directory. This is also available as top-level Makefile targets: `make all_adl`, `make all_ui`, `make all_opi`, `make all_bob`.

> convertIocFiles/
* Scripts intended to help convert an IOC directory from one version of synApps to another, by collecting data from an existing IOC directory and attempting to edit files in a new IOC directory.

> validateDB.py
* Validates EPICS database (.db) files for common errors.

> validateProto.py
* Validates StreamDevice protocol (.proto) files for common errors.

> dependencies.py
* Finds and displays dependencies between synApps modules.

> burt.py
* Python support for writing the content of a BURT snapshot file to a running IOC.

> mdautils-src/
* Utility programs for using MDA data files written by the __sscan__ module's saveData software.

> mdaExplorer/
* A wxPython program that displays the content of MDA files and directories of MDA files.

> mdaPythonUtils/
* A collection of python programs that read, write, modify, and translate MDA files.

> snapDb/
* A wxPython rapid development tool for EPICS databases and display files. Supports the use of EPICS' run-time programmability to prototype EPICS databases using records loaded into an IOC.


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
