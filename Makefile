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

define FILTER_TOP_LEVEL
  
  # Add module to build list if the directory it lives in is the same as
  # the support folder.
    
  ifeq ($(abspath $(SUPPORT)), $(abspath $(dir $(abspath $($(1))))))
  MODULE_LIST += $(1)
  endif
endef

define  MODULE_defined
  SUPPORT_DIRS  += $($(1))
  RELEASE_FILES += $($(1))/configure/RELEASE
  # areaDetector has differently named RELEASE files
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_LIBS.local)
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_LIBS.local.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_PRODS.local)
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE_PRODS.local.$(EPICS_HOST_ARCH))
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE.local)
  RELEASE_FILES += $(wildcard $($(1))/configure/RELEASE.local.$(EPICS_HOST_ARCH))
  $(eval $$($(1))_DEPEND_DIRS := $(shell $(GET_DEPENDS) $($(1)) $(1) "$(MODULE_LIST)"))
endef



############## DEPENDENCY GRAPH GENERATION ##############

# Filter out the module definitions that point to submodules
$(foreach mod, $(RELEASE_TOPS), $(eval $(call FILTER_TOP_LEVEL,$(mod)) ))

# Build the list of directories, RELEASE files, and dependencies
$(foreach mod, $(MODULE_LIST), $(eval $(call MODULE_defined,$(mod)) ))



################### BUILD DIRECTIONS #####################

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
