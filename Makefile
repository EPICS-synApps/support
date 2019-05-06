#FILENAME:      Makefile
#USAGE:         Top synApps Makefile
#Version:       $Revision$
#Modified By:   $Author$
#Last Modified: $Date$
#HeadURL:       $URL$

#NOTES
#     - The user must modify SUPPORT and EPICS_BASE in the
#       <synApps>/support/configure directory for the local configuration.
#
#     - To support multiple configurations, use multiple configure* directories
#
#     - Support modules can be shared between configurations only if
#       dependencies are not violated.  Only the "DIRS" are the target of
#       gnumake.  If this configuration is using a support module built by
#       another configuration, then the SUPPORT_DIRS line for that support
#       module must be commented out (i.e, must begin with a '#').
#
#     - To remove modules from the build, delete or comment out the module
#       in the <synApps>/configure/RELEASE file; not here.

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

MODULE_LIST =  ALLEN_BRADLEY 
MODULE_LIST += ALIVE 
MODULE_LIST += AREA_DETECTOR
MODULE_LIST += ASYN 
MODULE_LIST += AUTOSAVE 
MODULE_LIST += BUSY
MODULE_LIST += CALC 
MODULE_LIST += CAMAC
MODULE_LIST += CAPUTRECORDER
MODULE_LIST += DAC128V 
MODULE_LIST += DELAYGEN
MODULE_LIST += DEVIOCSTATS
MODULE_LIST += DXP 
MODULE_LIST += DXPSITORO 
MODULE_LIST += ETHERIP 
MODULE_LIST += IPAC 
MODULE_LIST += IP 
MODULE_LIST += IP330 
MODULE_LIST += IPUNIDIG 
MODULE_LIST += LOVE 
MODULE_LIST += LUA 
MODULE_LIST += MCA 
MODULE_LIST += MEASCOMP 
MODULE_LIST += MODBUS 
MODULE_LIST += MOTOR
MODULE_LIST += OPTICS 
MODULE_LIST += QUADEM 
MODULE_LIST += SNCSEQ
MODULE_LIST += SOFTGLUE 
MODULE_LIST += SOFTGLUEZYNQ 
MODULE_LIST += SSCAN 
MODULE_LIST += STD 
MODULE_LIST += STREAM 
MODULE_LIST += VAC 
MODULE_LIST += VME 
MODULE_LIST += XXX
MODULE_LIST += YOKOGAWA_DAS 

$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))

################### End of Support-Modules #####################

DIRS := $(DIRS) $(SUPPORT_DIRS)

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
