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
    
    
    - `xxx/iocBoot/ioc*/st.cmd.*` -- This is the file run by the IOC at boot time. It loads an executable built in the IOC directory (e.g., `xxx`, or `xxx.munch`), sets parameters to configure that software, makes calls to that software to configure it for a particular set of hardware, and loads databases from synApps modules. Mostly, it sources ioc shell files that do these same things.
        
        This file, and the files it sources, are probably worth studying. They are reasonably well commented, and contain `dbLoadRecords()` commands for most of the EPICS databases in synApps.
    - **Motors** -- To load more motors, add lines to the file `xxx/iocBoot/ioc*/motor.substitutions`. For motors controlled by a VME board, edit `vme.cmd` to specify the hardware address, etc. For motors controlled through a serial connection, edit `serial.cmd`.
        
        If you want the new motors to work with the 'AllStop' button (`xxx:allstop.VAL`-- see the top-level display `xxx.ui`), load the database `$(MOTOR)/db/motorUtil.db`, and run the command `motorUtilInit("xxx:")`.
        
        If you want the IOC automatically to save positions and settings of the new motors, and restore them when the crate reboots, add lines to the files `xxx/iocBoot/ioc*/auto_settings.req` and `xxx/iocBoot/ioc*/auto_positions.req`.
    - **Slits** -- To use a pair of motors to control a slit, search for `2slit.db`in `xxx/iocBoot/ioc*/examples/optics.iocsh`, and edit the `dbLoadRecords()` command you'll find there. The example in `optics.iocsh` loads two copies of `2slit.db` intended for use as the horizontal and vertical members of a four-jaw slit. The display files `2slit*` and `4slit*` are involved in these applications.
        
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
    - **Optical tables** -- Optical tables are controlled by a custom EPICS record (the "table" record), used in the database `table.db` and controlled via display files `table*.ui` (caQtDM) or `table*.adl` (MEDM).
        
        Table virtual motors behave in much the same way as do slit virtual motors. However, the table software does not use user/dial offsets in the underlying motor to implement recalibration (it can't, since it works through a nonlinear transform). Instead, the table maintains its own offsets for all of the six coordinated motions it implements. Pressing the "Set" button causes new table positions to modify the offsets instead of moving the table (which is exactly the way motor and slit calibration works). In addition to a "Sync" button, which reads motor positions and calculates the table positions from them, the table display has an "Init" button, which zeros all offsets before doing a "sync" operation. It also has a "Zero" button, which manipulates all the table offsets to make the current table positions zero without moving or recalibrating any motors.
    - **Monochromators** -- Several varieties of crystal monochromators are supported in synApps: two constant-offset "channel-cut" monochromators, two varieties of a high-resolution four-crystal monochromator, a spherical-grating monochromator, and a multilayer monochromator. Most are supported by databases paired with State Notation Language (SNL) programs, and display files. The EPICS databases `kohzuSeq.db`, SNL program `kohzuCtl.st`, and displays `kohzu*` are involved in control of two varieties of high-heat-load monochromators. The EPICS database `hrSeq.db`, SNL program `hrCtl.st`, and displays `hSeq*` are involved in control of the high-resolution double-crystal monochromator. The spherical grating monochromator is supported by the database `SGM.db` and the displays `SGM*`. The multilayer monochromator is supported by the database `ml_monoSeq.db` and displays `ml_mono*`.
    - **Filters** -- The APS standard user filters combine several motors and solenoids to control the placement of filter material in the beam path. The databases `filterMotor.db` and `filterLock.db`, and the display files `*filter*` are involved in this application.
        
        synApps also supports the XIA filter/shutter box, with two independently developed solutions:
        
        
        - pf4:   
            pf4\*.db  
            pf4\*.adl
        - filterbox:  
            filterBladeNoSensor.db, filterDrive.db  
            filter\_\*\_\*.adl, filterbox\_\*.adl filter\_drive\*.adl
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
