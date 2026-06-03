---
layout: default
title: Utils Directory
nav_order: 7
---


The synApps utils directory
---------------------------


The synApps support/utils directory contains a variety of scripts and programs that may be useful in administering and/or using synApps.

- **changePrefix** -- A perl script for changing EPICS PV-name prefixes in a user directory (e.g., when creating a new IOC from the __xxx__ template). You must be in the top level of the user directory to run it. Example of use:

    ```
    cd /path/to/ioc/1bm
    $(SYNAPPS)/support/utils/changePrefix xxx 1bma
    ```

- **copyScreens.pl** -- Search all synApps modules for display files and copy them to a single directory. This is also available as top-level Makefile targets: `make all_adl`, `make all_ui`, `make all_opi`, `make all_bob`.

- **convertIocFiles/** -- Scripts intended to help convert an IOC directory from one version of synApps to another, by collecting data from an existing IOC directory and attempting to edit files in a new IOC directory.

- **validateDB.py** -- Validates EPICS database (.db) files for common errors.

- **validateProto.py** -- Validates StreamDevice protocol (.proto) files for common errors.

- **dependencies.py** -- Finds and displays dependencies between synApps modules.

- **burt.py** -- Python support for writing the content of a BURT snapshot file to a running IOC.

- **mdautils-src/** -- Utility programs for using MDA data files written by the __sscan__ module's saveData software.

- **mdaExplorer/** -- A wxPython program that displays the content of MDA files and directories of MDA files.

- **mdaPythonUtils/** -- A collection of python programs that read, write, modify, and translate MDA files.

- **snapDb/** -- A wxPython rapid development tool for EPICS databases and display files. Supports the use of EPICS' run-time programmability to prototype EPICS databases using records loaded into an IOC.
