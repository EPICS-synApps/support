
DIRS += $(DXP)
RELEASE_FILES += $(DXP)/configure/RELEASE
$(DXP)_DEPEND_DIRS = $(CAMAC) $(MCA)

DIRS += $(QUADEM)
RELEASE_FILES += $(QUADEM)/configure/RELEASE
$(QUADEM)_DEPEND_DIRS = $(MCA)

DIRS += $(XXX)
RELEASE_FILES += $(XXX)/configure/RELEASE
$(XXX)_DEPEND_DIRS = $(DXP) $(QUADEM)

ACTIONS += uninstall realuninstall distclean cvsclean

include $(EPICS_BASE)/configure/RULES_TOP

release:
	echo SUPPORT=$(SUPPORT)
	echo ' '
	echo EPICS_BASE=$(EPICS_BASE)
	echo ' '
	echo MASTER_FILE=$(MASTER_FILE)
	echo ' '
	echo RELEASE_FILES=$(RELEASE_FILES)
	echo ' '
	$(PERL) $(TOP)/configure/makeReleaseConsistent.pl $(SUPPORT) $(EPICS_BASE) $(MASTER_FILE) $(RELEASE_FILES)

