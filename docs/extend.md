---
layout: default
title: Extending synApps
nav_order: 6
---


How to extend synApps
---------------------


Like all EPICS software, synApps can be extended in many ways, and at many levels, by EPICS developers and users. (That's how the package came to exist in the first place. It started as a single App directory, and folks just added stuff.) But synApps pushes the idea a little bit further toward end users who are not developers. One of the driving notions behind the development of synApps was to put as much of EPICS' flexibility and power as seems both wise and practical into the hands of end users – typically, scientists running experiments – whose backgrounds in software development and implementation vary over a wide range.

Here is a list of techniques by which synApps has already been extended by users and developers, arranged *very* roughly according to the amounts of effort, skill, and EPICS knowledge required.

- **Scaler end-calculation customization** -- This is certainly too simple to be considered an extension -- all you do is type something like "`(A-B)/I`" into a text box -- but it's still pretty useful, and it demonstrates a technique that will be used for much more sophisticated purposes.
- **Scan configuration** -- The first extension that many users attempt is the programming of a scan. This might also seem more like mere *use* than extension, but it can become a very highly evolved skill, and it is software development in a reasonably literal sense. If you buy into the notion that an EPICS database is essentially a program (in a very high-level programming language), then scan configuration can be viewed as the simpler end of a continuum.
- **"userCalc" programming** -- synApps facilitates run-time programming of a number of EPICS record types, by providing the following kinds of support:
    
    
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
- **[caputRecorder](https://github.com/epics-modules/caputRecorder/releases) macro recording** -- Users who know how to accomplish a task by executing or modifying EPICS records can write software to automate that task using caputRecorder:
    
    
    1. Enter a macro name to identify the task.
    2. Press caputRecorder's "Start" button.
    3. Perform the task manually.
    4. Press caputRecorder's "Stop" button.
- **Display editing** -- End users know better than anybody what they want in a graphical user interface. One thing they've demonstrated that they want is the ability to have some control over the user interface without having to specify every little detail to a programmer. caQtDM and Phoebus provide end users with the ability to create custom displays, and synApps provides over 800 user-interface files that can be copied from, called up from, or included as part of a user-crafted display.
- **IOC command-file editing** -- An EPICS IOC is populated and configured by ASCII command files, which knowledgeable end users can edit to add motors, change default baud rates, load additional copies of databases, etc.
- **Development of client-side scripts** -- Many synApps end users have written scripts, in languages such as the unix shell, Python, SPEC macro, IDL, tcl, perl, and Labview, to simplify and/or standardize beamline operations. Any language can be used for this purpose, if it can be fitted with a Channel-Access interface.
- **EPICS-database development** -- One very easy step from run-time programming to EPICS-database development can be taken by using the wxPython program, snapDb.py, (in the *utils* directory) to "freeze" a collection of programmed userCalcs into an independently loadable database. snapDb can also generate a first cut at a user interface for the database.

    But most EPICS database development is done with a database-configuration tool, such as VDCT, or with a text editor. In any case, EPICS-database development typically involves the selection of device support, the specification of links and link attributes, and the setting of parameters. More sophisticated development also involves the programming of an initialization strategy into the database, and maybe the writing of an autosave-request file, for it.
- **Development of subroutines** for the *sub* and *aSub* record types -- This is probably the simplest way to add custom C code to an EPICS application. SynApps contains several examples of this type of code, among them are arrayTest.c, interp.c, and subAve.c, all in the directory support/calc/calcApp/src.
- **Development of State-Notation-Language programs** -- This is probably the next easiest, and the next most capable, way of adding compiled code to an application. SNL also introduces to this list the notion of client-side program development, for an SNL program is a Channel Access client, even though it runs on an IOC. Again, synApps has many examples, which you can find by searching for ".st" and ".stt" files.

    Documentation for SNL can be found in the __seq__ module, a copy of which is bundled with synApps.
- **Device-support development** -- If synApps doesn't contain device support for the device you want to use, you can probably find (in synApps or elsewhere) a device-support example that has, at least, the structure of the sort of support you will need.

    Nobody writes device support from scratch; it's just not an effective way to develop. Everybody tries to find the closest approximation to what they need, and modifies it until it serves their purpose. One important use of the EPICS tech-talk email list is to gather suggestions, from folks further up the learning curve, on what might be a good piece of code to use or modify for a particular purpose.
- **Development of client-side GUI programs** -- This requires a lot of skill, effort, and information. Developers at this level need the *EPICS Application Developer's Guide*, the *Channel Access Reference Manual*, and very capable cross-platform GUI infrastructure.
- **Module development** -- This also requires a lot of skill, effort, and information. Developers at this level need the *EPICS Application Developer's Guide*, and the *EPICS Record Reference Manual*. One of the very best features of EPICS is the fact that experts in module development can collaborate with experts in client-side development, even if the developers are unaware of each other.

All of the extension strategies described above produce (or, at least *can* produce) results which are *fully* integrated into the control system. This means that they can be used in further extensions by the same techniques. Thus, for example, motors ganged together by a transform record can be scanned, driven by a PID loop, or controlled by another userCalc.
