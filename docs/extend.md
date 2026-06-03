---
layout: default
title: Extending synApps
nav_order: 5
---


How to extend synApps
---------------------


Like all EPICS software, synApps can be extended in many ways, and at many levels, by EPICS developers and users. synApps pushes the idea a little bit further toward end users who are not developers. One of the driving notions behind the development of synApps was to put as much of EPICS' flexibility and power as seems both wise and practical into the hands of end users -- typically, scientists running experiments -- whose backgrounds in software development and implementation vary over a wide range.

Here is a list of techniques by which synApps has been extended by users and developers, arranged roughly by the amount of effort, skill, and EPICS knowledge required.

### Run-time programming

synApps modules provide many records and databases designed for end-user programming at run time, some of these include:

- **userCalcs** (swait, calcout, sCalcout, aCalcout, transform records) -- See the [calc module documentation](https://epics-modules.github.io/calc/)
- **Scans** -- See the [sscan module documentation](https://epics-modules.github.io/sscan/)
- **PID / feedback loops** -- See the [std module documentation](https://epics-modules.github.io/std/)
- **Macro recording** -- See the [caputRecorder documentation](https://epics-modules.github.io/caputRecorder/)
- **Impromptu device support** -- See the [ip module documentation](https://epics-modules.github.io/ip/) (`deviceCmdReply.db`)
- **Scripting** -- See the [lua module documentation](https://epics-modules.github.io/lua/)

### Display and IOC editing

- **Display editing** -- caQtDM and Phoebus allow end users to create custom displays. synApps provides over 800 display files as starting points.
- **IOC command-file editing** -- IOC startup scripts (`.cmd`, `.iocsh`) are ASCII files that can be edited to add hardware, load databases, change parameters, etc.

### Client-side scripting

Any language with a Channel Access or PV Access interface (Python, SPEC, shell scripts, etc.) can be used to automate beamline operations.

### Software development

For more advanced extensions, including EPICS database development, sub/aSub record subroutines, State Notation Language (SNL) programs, device support, and module development, see the [EPICS Application Developer's Guide](https://docs.epics-controls.org/en/appdevguide/gettingStarted.html) and the individual module documentation at [epics-modules.github.io](https://epics-modules.github.io/).

---

All of the extension strategies described above produce (or, at least *can* produce) results which are fully integrated into the control system. This means that they can be used in further extensions by the same techniques. For example, motors ganged together by a transform record can be scanned, driven by a PID loop, or controlled by another userCalc.
