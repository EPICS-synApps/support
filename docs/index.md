---
layout: default
title: Home
nav_order: 1
---


synApps 6.4
===========


Introduction
------------

- - - - - -

synApps is a collection of [EPICS](https://epics.anl.gov/) software intended to support most of the common requirements of an x-ray laboratory or synchrotron-radiation beamline. Because it is EPICS software, synApps is extensible by developers and end users, to support new devices and experimental techniques. This extensibility frees synApps to focus mostly on general-purpose capabilities and infrastructure, from which application-specific software can be built or assembled.

> Thus, for example, synApps provides support for motors, scalers, and scans, but it does not tie those items together into an immediately executable scan (of specific motors, to acquire specific scaler channels, for a specific dwell time, etc.). The user does this at run time (or a knowledgeable user can provide a fully specified scan, and give the novice user a button to start it).
> 
> Similarly, synApps provides support for ADC's and PID loops, but somebody has to tell the PID software what feedback value to read, what conditioning function to run it through, what PID parameters to use, and what actuator to drive. By default, all of these choices can be made at top level, by the end user. Or, a knowledgeable user can provide a fully specified PID loop, and make it available to a novice user through a simplified or otherwise customized interface. The techniques and tools used to accomplish this are essentially the same as those a user would have applied at run time, so the packaged solution can be prototyped and tested at run time.

synApps is organized into modules, whose structure is based on the example directory tree produced by the EPICS application, `makeBaseApp.pl`, typically with two additional directories: a documentation directory, and a display-file directory. synApps modules typically contain source code, EPICS databases and database-definition files, autosave-request files, client scripts, display files, libraries and executables, and documentation.

**Getting Started:**
- [Deploying synApps](deploy.html) -- How to obtain and build synApps
- [Configuring an IOC](configure.html) -- Setting up and running an IOC with synApps
- [Extending synApps](extend.html) -- From run-time programming to module development
- [Utils Directory](utils.html) -- Utility scripts and tools
- [Release Notes](synAppsReleaseNotes.html) -- Version history
- [Documentation Links](synApps_docs_all.html) -- Links to all module documentation

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
    
    [Appended as a separate page](device_support.html).
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
    
    The synApps support/utils directory contains a variety of scripts, programs, etc., that some have found useful. See the [utils directory](utils.html) page for details.


- - - - - -

 Suggestions and Comments to:   
 [Keenan Lang](mailto:klang@anl.gov) (klang@anl.gov)   
 Beamline Controls & Data Acquisition Group  
 Advanced Photon Source, Argonne National Laboratory
