---
layout: default
title: Device Support
nav_order: 11
---


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
