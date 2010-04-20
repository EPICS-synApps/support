#FILENAME:	Makefile
#USAGE:		Top Makefile
#Version:	$Revision: 1.14 $
#Modified By:	$Author: mooney $
#Last Modified:	$Date: 2009-03-06 20:20:43 $
#NOTES- The "SUPPORT_DIRS" order is based on compile time dependencies.
#     - The user must modify SUPPORT and EPICS_BASE in the
#       <synApps>/support/configure directory for the local configuration.
#     - To support multiple configurations, use multiple configure* directories
#     - Support modules can be shared between configurations only if
#	dependencies are not violated.  Only the "DIRS" are the target of
#	gnumake.  If this configuration is using a support module built by
#	another configuration, then the	SUPPORT_DIRS line for that support
#	module must be commented out (i.e, must begin with a '#').

# Note the only dependencies that matter in $(<module>)_DEPEND_DIRS are
# compile-time dependencies.

TOP = .

MASTER_FILE = $(TOP)/configure/RELEASE

include $(TOP)/configure/CONFIG

###### 1st Tier Support Modules - Only Depend on EPICS BASE ######

SUPPORT_DIRS += $(VXSTATS)
RELEASE_FILES += $(VXSTATS)/configure/RELEASE

SUPPORT_DIRS += $(SNCSEQ)
RELEASE_FILES += $(SNCSEQ)/configure/RELEASE

ifdef ALLEN_BRADLEY
	SUPPORT_DIRS += $(ALLEN_BRADLEY)
	RELEASE_FILES += $(ALLEN_BRADLEY)/configure/RELEASE
endif

SUPPORT_DIRS += $(IPAC)
RELEASE_FILES += $(IPAC)/configure/RELEASE

SUPPORT_DIRS += $(SSCAN)
RELEASE_FILES += $(SSCAN)/configure/RELEASE

SUPPORT_DIRS += $(AUTOSAVE)
RELEASE_FILES += $(AUTOSAVE)/configure/RELEASE

###### 2nd Tier Support Modules - Only Depend on 1st Tier ########

SUPPORT_DIRS += $(ASYN)
RELEASE_FILES += $(ASYN)/configure/RELEASE
$(ASYN)_DEPEND_DIRS = $(SNCSEQ) $(IPAC)

SUPPORT_DIRS += $(CALC)
RELEASE_FILES += $(CALC)/configure/RELEASE
$(CALC)_DEPEND_DIRS = $(SSCAN)

################### 3rd Tier Support Modules #####################

SUPPORT_DIRS += $(BUSY)
RELEASE_FILES += $(BUSY)/configure/RELEASE
$(BUSY)_DEPEND_DIRS = $(ASYN)

SUPPORT_DIRS += $(MOTOR)
RELEASE_FILES += $(MOTOR)/configure/RELEASE
$(MOTOR)_DEPEND_DIRS = $(ASYN) $(SNCSEQ) $(IPAC)

SUPPORT_DIRS += $(STD)
RELEASE_FILES += $(STD)/configure/RELEASE
$(STD)_DEPEND_DIRS = $(ASYN)

SUPPORT_DIRS += $(DAC128V)
RELEASE_FILES += $(DAC128V)/configure/RELEASE
$(DAC128V)_DEPEND_DIRS = $(ASYN)  $(IPAC)

SUPPORT_DIRS += $(IP330)
RELEASE_FILES += $(IP330)/configure/RELEASE
$(IP330)_DEPEND_DIRS = $(ASYN) $(IPAC)

SUPPORT_DIRS += $(IPUNIDIG)
RELEASE_FILES += $(IPUNIDIG)/configure/RELEASE
$(IPUNIDIG)_DEPEND_DIRS = $(ASYN) $(IPAC)

SUPPORT_DIRS += $(LOVE)
RELEASE_FILES += $(LOVE)/configure/RELEASE
$(LOVE)_DEPEND_DIRS = $(ASYN) $(IPAC)

SUPPORT_DIRS += $(IP)
RELEASE_FILES += $(IP)/configure/RELEASE
$(IP)_DEPEND_DIRS = $(ASYN) $(IPAC) $(SNCSEQ)

SUPPORT_DIRS += $(OPTICS)
RELEASE_FILES += $(OPTICS)/configure/RELEASE
$(OPTICS)_DEPEND_DIRS = $(ASYN)

SUPPORT_DIRS += $(STREAM)
RELEASE_FILES += $(STREAM)/configure/RELEASE
$(STREAM)_DEPEND_DIRS = $(ASYN) $(CALC) $(SSCAN)

SUPPORT_DIRS += $(MODBUS)
RELEASE_FILES += $(MODBUS)/configure/RELEASE
$(MODBUS)_DEPEND_DIRS = $(ASYN)

SUPPORT_DIRS += $(VAC)
RELEASE_FILES += $(VAC)/configure/RELEASE
$(VAC)_DEPEND_DIRS = $(ASYN) $(IPAC)

SUPPORT_DIRS += $(SOFTGLUE)
RELEASE_FILES += $(SOFTGLUE)/configure/RELEASE
$(SOFTGLUE)_DEPEND_DIRS = $(ASYN) $(IPAC)

################### 4th Tier Support Modules #####################

SUPPORT_DIRS += $(DELAYGEN)
RELEASE_FILES += $(DELAYGEN)/configure/RELEASE
$(DELAYGEN)_DEPEND_DIRS = $(ASYN) $(STD)

SUPPORT_DIRS += $(CAMAC)
RELEASE_FILES += $(CAMAC)/configure/RELEASE
$(CAMAC)_DEPEND_DIRS = $(MOTOR) $(STD)

SUPPORT_DIRS += $(MCA)
RELEASE_FILES += $(MCA)/configure/RELEASE
$(MCA)_DEPEND_DIRS = $(ASYN) $(STD)

SUPPORT_DIRS += $(VME)
RELEASE_FILES += $(VME)/configure/RELEASE
$(VME)_DEPEND_DIRS = $(STD)

#!SUPPORT_DIRS += $(EBRICK)
#!RELEASE_FILES += $(EBRICK)/configure/RELEASE
#!$(EBRICK)_DEPEND_DIRS = $(STD)

################### 5th Tier Support Modules #####################

SUPPORT_DIRS += $(AREA_DETECTOR)
RELEASE_FILES += $(AREA_DETECTOR)/configure/RELEASE
$(AREA_DETECTOR)_DEPEND_DIRS = $(ASYN) $(SSCAN) $(MCA)

SUPPORT_DIRS += $(QUADEM)
RELEASE_FILES += $(QUADEM)/configure/RELEASE
$(QUADEM)_DEPEND_DIRS = $(ASYN) $(MCA)

################### 6th Tier Support Modules #####################

SUPPORT_DIRS += $(DXP)
RELEASE_FILES += $(DXP)/configure/RELEASE
$(DXP)_DEPEND_DIRS = $(AREA_DETECTOR) $(ASYN) $(CAMAC) $(MCA) $(BUSY)

################### End of Support-Modules #####################

DIRS = $(SUPPORT_DIRS)

################### User Modules #####################

DIRS += $(XXX)
RELEASE_FILES += $(XXX)/configure/RELEASE
$(XXX)_DEPEND_DIRS = $(SUPPORT_DIRS)

#DIRS += $(IP_USE)
#RELEASE_FILES += $(IP_USE)/configure/RELEASE
#$(IP_USE)_DEPEND_DIRS = $(SUPPORT_DIRS)



ACTIONS += uninstall realuninstall distclean cvsclean

include $(EPICS_BASE)/configure/RULES_TOP

release:
	echo SUPPORT=$(SUPPORT)
	echo ' '
	echo EPICS_BASE=$(EPICS_BASE)
	echo ' '
	echo MASTER_FILE=$(MASTER_FILE)
	echo ' '
	echo DIRS=$(DIRS)
	echo ' '
	echo RELEASE_FILES=$(RELEASE_FILES)
	echo ' '
	$(PERL) $(TOP)/configure/makeReleaseConsistent.pl $(SUPPORT) $(EPICS_BASE) $(MASTER_FILE) $(RELEASE_FILES)

