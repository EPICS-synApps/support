---
layout: default
title: vxWorks Configuration
nav_order: 9
---


vxWorks IOC Configuration
=========================

This page covers the setup and configuration of vxWorks-based VME IOCs for use with synApps. For Linux soft IOC deployment, see the main [synApps Overview](index.html).


Setting up the IOC
------------------

Ensure that `$(EPICS_BASE)/bin/<arch>/caRepeater` is running on your workstation. If you have no way of starting it automatically at boot, you can run it manually or add the command to your login script.

### Serial console setup

Connect a serial cable from your workstation to the VME processor's "Console" port. Configure a terminal emulator (e.g., `minicom`, `screen`, or `cu`) to connect at 9600 baud. For example:

```
cu -lttya
```

or

```
screen /dev/ttyS0 9600
```

### Boot parameters

Turn the crate on. The crate processor will display "Press any key to stop auto-boot..." with a countdown. Pressing a key gets the prompt `[VxWorks Boot]:`.

Type `p` to view the current boot parameters, or `c` to change them. Here are sample boot parameters:

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
    startup script (s)   : /path/to/ioc/iocBoot/iocxxx/st.cmd
    other (o)            :
```

See `xxx/iocBoot/ioc*/bootParms` for examples for other processor types.


NFS and file system considerations
-----------------------------------

vxWorks IOCs typically access their startup scripts and databases via NFS-mounted file systems. Ensure that:

- The NFS export is accessible from the IOC's network.
- The IOC user has read access to the application directory.
- For autosave, the IOC must have write access to the autosave directory. You must use a version of vxWorks that can append to files via NFS (vxWorks 6.9.4.1 or later is known to work).

If your IOC and host use different paths to access the application directory (e.g., when booting from a Microsoft FTP server or certain NFS configurations), set `IOCS_APPL_TOP` in `support/configure/CONFIG_SITE` and rebuild the iocBoot directory.


autosave on vxWorks
-------------------

For vxWorks IOCs, the autosave directory must be writable via NFS:

```
chmod a+w,g+s autosave
```

It is helpful to set the group sticky bit so that files written by the IOC process are owned by the directory's group rather than the IOC user.

If you are using autosaveBuild, the IOC must also have write permission to the directory where autosave request files are generated.

