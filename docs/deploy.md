---
layout: default
title: Deploying synApps
nav_order: 2
---


# Deploying and Building synApps
{: .no_toc}

## Table of contents
{: .no_toc .text-delta }

- TOC
{:toc}

## How to deploy synApps

synApps is normally deployed as a two-part system: a 'support' directory, and one or more 'user' directories. The support directory can be installed on a read-only file system, along with EPICS base and other modules, and used from there by user directories. Each user directory typically begins as a copy of the __xxx__ module, customized and extended to suit a particular application and set of hardware.

There are two ways to obtain the synApps support directory:

### Option 1: Download a prebuilt tarball

Download a release tarball from the [synApps releases page](https://github.com/EPICS-synApps/support/releases). This provides a pre-assembled support directory with all modules at tested, compatible versions.

### Option 2: Use the assemble_synApps script

The [assemble_synApps](https://github.com/EPICS-synApps/assemble_synApps) perl script will clone all synApps modules from GitHub at compatible versions and configure them to build together. This is the recommended approach for users who want to customize which modules are included or track specific module versions.

The script can be configured to select module versions, enable or disable specific modules, and set the path to EPICS base. See the [assemble_synApps documentation](https://github.com/EPICS-synApps/assemble_synApps) for details.

### The support directory

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

### The user directory

A user directory is typically constructed from the __xxx__ module, which serves as a template. At its simplest, a single copy of __xxx__ supports a single IOC. If several IOCs cooperate to serve a single application (such as a synchrotron beamline), one might make several independent copies of __xxx__, or extend a single copy to contain multiple xxxApp directories and multiple iocBoot/iocxxx directories.

To create a user directory from the __xxx__ template, copy the __xxx__ module directory, then run `changePrefix` to rename all PV prefixes:

```
    cp -r $(SYNAPPS)/support/xxx /path/to/ioc/1bm
    cd /path/to/ioc/1bm
    $(SYNAPPS)/support/utils/changePrefix xxx 1bma
```

Then edit the following files to configure the user directory:

- `1bm/configure/RELEASE` -- Edit the definition of `SUPPORT` with the correct path to the support directory.
- `1bm/iocBoot/ioc1bma/*.cmd`, `1bm/iocBoot/ioc1bma/*.iocsh` -- Configure hardware, load databases, and set IOC parameters.
- `1bm/setup_epics_common` -- Set the value of Channel Access environment variables.
- `1bm/start_caQtDM_1bma` or `1bm/start_phoebus_1bma` -- Edit to specify the path to the application and display-file directories.

The association between a user directory and the support directory on which it depends is made entirely by the file `configure/RELEASE` in the user directory.

{: .note }
> The modules in synApps are interdependent. Many of the modules depend on the __asyn__ module, for example, and there are many other dependencies, both direct and implied. The complete set of modules selected by a user directory must be self consistent, and the EPICS build will ensure this, unless you tell it not to, by defining `CHECK_RELEASE=NO` or `CHECK_RELEASE=WARN` in `configure/CONFIG_SITE`.

The synApps build imposes an additional constraint on module names. Because synApps uses EPICS build rules to descend from `support` into the modules, module names may not include the character '.'. (The EPICS build rules expect '.' to be followed by a host or target architecture.)



## How to build synApps


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

3. **Building a user directory.** Once the support directory has built, the __xxx__ module will have been configured and built. Copy it, run `changePrefix`, edit the configuration files as described [above](<#How to deploy synApps>), and run `make`.


## Configuring and running the IOC

Once you have created a user directory from the __xxx__ template, see the [xxx module documentation](https://epics-modules.github.io/xxx/configuring.html) for details on:

- Setting up and starting the IOC (Linux soft IOC or vxWorks)
- Configuring hardware (motors, optics, serial devices, detectors)
- Display managers (caQtDM, Phoebus, MEDM)
- autosave/restore
- saveData scan-data writing
