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
  endif  
endef


###### 1st Tier Support Modules - Only Depend on EPICS BASE ######

#MODULE_LIST  = VXSTATS SNCSEQ ALLEN_BRADLEY
MODULE_LIST  = DEVIOCSTATS SNCSEQ ALLEN_BRADLEY
MODULE_LIST += IPAC SSCAN AUTOSAVE
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

###### 2nd Tier Support Modules - Only Depend on 1st Tier ########

MODULE_LIST  = ASYN CALC
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(ASYN)_DEPEND_DIRS = $(SNCSEQ) $(IPAC)
$(CALC)_DEPEND_DIRS = $(SSCAN)

################### 3rd Tier Support Modules #####################

MODULE_LIST  = BUSY MOTOR STD DAC128V IP330 IPUNIDIG LOVE
MODULE_LIST += IP OPTICS STREAM MODBUS VAC SOFTGLUE QUADEM
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(BUSY)_DEPEND_DIRS     = $(ASYN)
$(MOTOR)_DEPEND_DIRS    = $(ASYN) $(SNCSEQ) $(IPAC)
$(STD)_DEPEND_DIRS      = $(ASYN)
$(DAC128V)_DEPEND_DIRS  = $(ASYN) $(IPAC)
$(IP330)_DEPEND_DIRS    = $(ASYN) $(IPAC)
$(IPUNIDIG)_DEPEND_DIRS = $(ASYN) $(IPAC)
$(LOVE)_DEPEND_DIRS     = $(ASYN) $(IPAC)
$(IP)_DEPEND_DIRS       = $(ASYN) $(IPAC) $(SNCSEQ)
$(OPTICS)_DEPEND_DIRS   = $(ASYN)
$(STREAM)_DEPEND_DIRS   = $(ASYN) $(CALC) $(SSCAN)
$(MODBUS)_DEPEND_DIRS   = $(ASYN)
$(VAC)_DEPEND_DIRS      = $(ASYN) $(IPAC)
$(SOFTGLUE)_DEPEND_DIRS = $(ASYN) $(IPAC)
$(QUADEM)_DEPEND_DIRS   = $(ASYN)

################### 4th Tier Support Modules #####################

#MODULE_LIST  = DELAYGEN CAMAC MCA VME EBRICK
MODULE_LIST  = DELAYGEN CAMAC MCA VME
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(DELAYGEN)_DEPEND_DIRS = $(STD) $(STREAM)
$(CAMAC)_DEPEND_DIRS    = $(MOTOR) $(STD)
$(MCA)_DEPEND_DIRS      = $(BUSY) $(CALC) $(STD)
$(VME)_DEPEND_DIRS      = $(STD)
#$(EBRICK)_DEPEND_DIRS   = $(STD) $(CALC)

################### 5th Tier Support Modules #####################
# The conditional below should be a target arch, but those are not
# defined at this level.
ifneq (solaris,$(findstring solaris, $(EPICS_HOST_ARCH)))
MODULE_LIST = AREA_DETECTOR
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(AREA_DETECTOR)_DEPEND_DIRS = $(ASYN) $(SSCAN) $(MCA)
endif
################### 6th Tier Support Modules #####################
# The conditional below should be a target arch, but those are not
# defined at this level.
ifneq (solaris,$(findstring solaris, $(EPICS_HOST_ARCH)))
MODULE_LIST = DXP
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

$(DXP)_DEPEND_DIRS = $(AREA_DETECTOR) $(ASYN) $(CAMAC) $(MCA) $(BUSY)
endif
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

