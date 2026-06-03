---
layout: default
title: Configuring an IOC
nav_order: 3
---


Configuring and Running a synApps IOC
=====================================


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

    - `xxx/iocBoot/ioc*/st.cmd.*` -- The IOC's startup script; it loads the other .cmd files.
    - `xxx/iocBoot/ioc*/examples/*.iocsh` -- Example command files that can be invoked by st.cmd.
    - `xxx/iocBoot/ioc*/substitutions/*.substitutions` -- Database substitution files.
    - `xxx/iocBoot/ioc*/auto_positions.req`, `xxx/iocBoot/ioc*/auto_settings.req` -- Specify PVs to be saved periodically during operation and restored automatically when the IOC is rebooted. (These can also be constructed automatically during boot; see [autosaveBuild](https://epics-modules.github.io/autosave/) in the autosave documentation.)
    - `xxx/iocBoot/ioc*/saveData.req` -- Identifies PVs used by the saveData software, sscan records to be monitored for data, and PVs whose values are to be included in all scan-data files.
    
    __In more detail__
    
    
    - `xxx/iocBoot/ioc*/st.cmd.*` -- This is the file run by the IOC at boot time. It loads an executable built in the IOC directory, sets parameters to configure that software, makes calls to configure it for a particular set of hardware, and loads databases from synApps modules. Mostly, it sources `.iocsh` files that do these same things. This file, and the files it sources, are worth studying -- they are well commented and contain `dbLoadRecords()` commands for most of the EPICS databases in synApps.

    - **Motors** -- Motor configuration is done through substitution files and startup scripts. See the [motor module documentation](https://epics-modules.github.io/motor/) for details. In the xxx template, motor substitution files are at `xxx/iocBoot/ioc*/motor.substitutions`.

    - **Slits, optical tables, monochromators, filters** -- These optics devices are configured through database loading and SNL programs in the IOC startup scripts. See the [optics module documentation](https://epics-modules.github.io/optics/) for detailed usage of slit (`2slit.db`), table (`table.db`), monochromator (`kohzuSeq.db`, `hrSeq.db`, `SGM.db`, `ml_monoSeq.db`), and filter (`pf4`, `filterMotor.db`) databases and displays.

    synApps also includes many features for run-time programming, including userCalcs, string and array expression evaluation, scan support, sequence records, signal averaging, interpolation, and FPGA-based digital logic. See [Extending synApps](extend.html) for details on these capabilities.
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
