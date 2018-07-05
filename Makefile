#FILENAME:      Makefile
#USAGE:         Top synApps Makefile
#Version:       $Revision$
#Modified By:   $Author$
#Last Modified: $Date$
#HeadURL:       $URL$

#NOTES
#     - The "MODULE_LIST" order is based on compile time dependencies.
#     - The user must modify SUPPORT and EPICS_BASE in the
#       <synApps>/support/configure directory for the local configuration.
#     - To support multiple configurations, use multiple configure* directories
#     - Support modules can be shared between configurations only if
#       dependencies are not violated.  Only the "DIRS" are the target of
#       gnumake.  If this configuration is using a support module built by
#       another configuration, then the SUPPORT_DIRS line for that support
#       module must be commented out (i.e, must begin with a '#').
#     - To remove modules from the build, delete or comment out the module
#       in the <synApps>/configure/RELEASE file; not here.

# Note the only dependencies that matter in $(<module>)_DEPEND_DIRS are
# compile-time dependencies.

TOP = .

MASTER_FILE = $(TOP)/configure/RELEASE

include $(TOP)/configure/CONFIG

DIRS := $(DIRS) $(filter-out $(DIRS), configure)

define  MODULE_defined
  ifdef $(1)
  SUPPORT_DIRS  += $($(1))
  RELEASE_FILES += $($(1))/configure/RELEASE
  # areaDetector has differently named RELEASE files
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_BASE.local)
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_BASE.local.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_BASE.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_SUPPORT.local)
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_SUPPORT.local.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_SUPPORT.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_PATHS.local)
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_PATHS.local.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_PATHS.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_LIBS.local)
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_LIBS.local.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_LIBS.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_PRODS.local)
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_PRODS.local.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_PRODS.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE.local)
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE.local.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE.$(EPICS_HOST_ARCH))
  endif  
endef


###### 1st Tier Support Modules - Only Depend on EPICS BASE ######

MODULE_LIST =  SNCSEQ ALLEN_BRADLEY
MODULE_LIST += IPAC AUTOSAVE ALIVE CAPUTRECORDER
MODULE_LIST += ETHERIP
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

###### 1.5 Tier Support Modules - Only Depend on 1st Tier ######
# sscan now depends on seq, via scanProgress.st, but sscan can also build
# without seq. Yokogawa DAS can also build without seq.
MODULE_LIST = SSCAN DEVIOCSTATS YOKOGAWA_DAS
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))
$(SSCAN)_DEPEND_DIRS     = $(SNCSEQ)
$(DEVIOCSTATS)_DEPEND_DIRS     = $(SNCSEQ)
$(YOKOGAWA_DAS)_DEPEND_DIRS = $(SNCSEQ)

###### 2nd Tier Support Modules - Only Depend on 1st Tier ########

MODULE_LIST  = ASYN CALC
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(ASYN)_DEPEND_DIRS = $(SNCSEQ) $(IPAC)
$(CALC)_DEPEND_DIRS = $(SNCSEQ) $(SSCAN)

################### 3rd Tier Support Modules #####################

MODULE_LIST  = BUSY STD DAC128V IP330 IPUNIDIG LOVE
MODULE_LIST += IP OPTICS STREAM MODBUS VAC SOFTGLUE
MODULE_LIST += LUA
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(BUSY)_DEPEND_DIRS     = $(ASYN)
$(STD)_DEPEND_DIRS      = $(ASYN) $(SNCSEQ)
$(DAC128V)_DEPEND_DIRS  = $(ASYN) $(IPAC)
$(IP330)_DEPEND_DIRS    = $(ASYN) $(IPAC)
$(IPUNIDIG)_DEPEND_DIRS = $(ASYN) $(IPAC)
$(LOVE)_DEPEND_DIRS     = $(ASYN) $(IPAC)
$(IP)_DEPEND_DIRS       = $(ASYN) $(IPAC) $(SNCSEQ)
$(OPTICS)_DEPEND_DIRS   = $(ASYN) $(SNCSEQ)
$(STREAM)_DEPEND_DIRS   = $(ASYN) $(CALC) $(SSCAN)
$(MODBUS)_DEPEND_DIRS   = $(ASYN)
$(VAC)_DEPEND_DIRS      = $(ASYN) $(IPAC)
$(SOFTGLUE)_DEPEND_DIRS = $(ASYN) $(IPAC)
$(LUA)_DEPEND_DIRS      = $(ASYN)

################### 4th Tier Support Modules #####################

MODULE_LIST  = DELAYGEN MCA VME MOTOR AREA_DETECTOR SOFTGLUEZYNQ
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(DELAYGEN)_DEPEND_DIRS = $(ASYN) $(AUTOSAVE) $(CALC) $(IP) $(IPAC) $(STREAM) 
$(MCA)_DEPEND_DIRS      = $(ASYN) $(AUTOSAVE) $(BUSY) $(CALC) $(SNCSEQ) $(SSCAN) $(STD)
$(VME)_DEPEND_DIRS      = $(SNCSEQ) $(STD)
$(MOTOR)_DEPEND_DIRS    = $(ASYN) $(BUSY) $(IPAC) $(SNCSEQ) 
$(AREA_DETECTOR)_DEPEND_DIRS = $(ASYN) $(AUTOSAVE) $(BUSY) $(CALC) $(SSCAN)
$(SOFTGLUEZYNQ)_DEPEND_DIRS = $(ASYN) $(SNCSEQ) $(STD)
#$(EBRICK)_DEPEND_DIRS   = $(ASYN) $(AUTOSAVE) $(CALC) $(SNCSEQ) $(SSCAN) $(STD)

################### 4.5th Tier Support Modules #####################

MODULE_LIST  = MEASCOMP
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(MEASCOMP)_DEPEND_DIRS   = $(ASYN) $(CALC) $(STD) $(MCA) $(BUSY) $(SSCAN) $(AUTOSAVE) $(SNCSEQ)  

################### 5th Tier Support Modules #####################
# The conditional below should be a target arch, but those are not
# defined at this level.
MODULE_LIST = CAMAC QUADEM
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(CAMAC)_DEPEND_DIRS    = $(CALC) $(SSCAN) $(MOTOR) $(STD)
$(QUADEM)_DEPEND_DIRS   = $(AREA_DETECTOR) $(ASYN) $(AUTOSAVE) $(BUSY) $(IPAC) $(IPUNIDIG) $(MCA) $(SNCSEQ)

################### 6th Tier Support Modules #####################
# The conditional below should be a target arch, but those are not
# defined at this level.
MODULE_LIST = DXP DXPSITORO
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(DXP)_DEPEND_DIRS = $(AREA_DETECTOR) $(ASYN) $(AUTOSAVE) $(BUSY) $(CALC) $(CAMAC) $(MCA) $(SNCSEQ) $(SSCAN)
$(DXPSITORO)_DEPEND_DIRS = $(AREA_DETECTOR) $(ASYN) $(AUTOSAVE) $(BUSY) $(CALC) $(CAMAC) $(MCA) $(SNCSEQ) $(SSCAN)

################### End of Support-Modules #####################

DIRS = $(SUPPORT_DIRS)

################### User Modules #####################

ifdef XXX
DIRS += $(XXX)
RELEASE_FILES += $(XXX)/configure/RELEASE
$(XXX)_DEPEND_DIRS = $(SUPPORT_DIRS)
endif

ACTIONS += uninstall realuninstall distclean cvsclean

include $(TOP)/configure/RULES_TOP

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

