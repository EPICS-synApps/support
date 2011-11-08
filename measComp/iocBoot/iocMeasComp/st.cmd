< envPaths

## Register all support components
dbLoadDatabase "../../dbd/measCompApp.dbd"
measCompApp_registerRecordDeviceDriver pdbbase

## Configure port driver
C9513Config("C9513_1", 0, 2)
dbLoadTemplate("C9513.substitutions")

## Configure port driver
USB1608GConfig("1608G_1", 1, 1000000, 1000000)
dbLoadTemplate("1608G.substitutions")

#asynSetTraceMask 1608G_1 -1 255

< save_restore.cmd

iocInit

create_monitor_set("auto_settings.req",30)
