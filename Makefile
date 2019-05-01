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

GET_DEPENDS := $(SUPPORT)/utils/depends.pl $(call FIND_TOOL,convertRelease.pl)

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
  $(eval $$($(1))_DEPEND_DIRS := $(shell $(GET_DEPENDS) $($(1)) $(1) "$(MODULE_LIST)"))
  endif  
endef

###### Support Modules ######

MODULE_LIST =  SNCSEQ ALLEN_BRADLEY IPAC 
MODULE_LIST += AUTOSAVE ALIVE CAPUTRECORDER
MODULE_LIST += ETHERIP SSCAN DEVIOCSTATS
MODULE_LIST += YOKOGAWA_DAS ASYN CALC BUSY
MODULE_LIST += STD DAC128V IP330 IPUNIDIG 
MODULE_LIST += LOVE IP OPTICS STREAM MODBUS 
MODULE_LIST += VAC SOFTGLUE LUA DELAYGEN
MODULE_LIST += MCA VME MOTOR AREA_DETECTOR
MODULE_LIST += SOFTGLUEZYNQ MEASCOMP CAMAC
MODULE_LIST += QUADEM DXP DXPSITORO XXX
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

################### End of Support-Modules #####################

DIRS = $(SUPPORT_DIRS)

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


.PHONY: all_adl all_edl all_ui all_opi
	
all_adl:
	$(PERL) $(TOP)/utils/copyScreens.pl $(SUPPORT) 'adl'
	
all_edl:
	$(PERL) $(TOP)/utils/copyScreens.pl $(SUPPORT) 'edl'
	
all_ui:
	$(PERL) $(TOP)/utils/copyScreens.pl $(SUPPORT) 'ui,qss'
	
all_opi:
	$(PERL) $(TOP)/utils/copyScreens.pl $(SUPPORT) 'opi'
