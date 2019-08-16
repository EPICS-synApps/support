TOP=..

# Allow user to override where the build rules come from
RULES = $(EPICS_BASE)

# RELEASE files point to other application tops
include $(TOP)/configure/RELEASE
-include $(TOP)/configure/RELEASE.$(EPICS_HOST_ARCH)
-include $(TOP)/configure/RELEASE.$(EPICS_HOST_ARCH).Common
ifdef T_A
-include $(TOP)/configure/RELEASE.Common.$(T_A)
-include $(TOP)/configure/RELEASE.$(EPICS_HOST_ARCH).$(T_A)
endif

override undefine SUPPORT

CONFIG = $(RULES)/configure
include $(CONFIG)/CONFIG

# Override the Base definition:
INSTALL_LOCATION = $(TOP)

# CONFIG_SITE files contain other build configuration settings
include $(TOP)/configure/CONFIG_SITE
-include $(TOP)/configure/CONFIG_SITE.$(EPICS_HOST_ARCH)
-include $(TOP)/configure/CONFIG_SITE.$(EPICS_HOST_ARCH).Common
ifdef T_A
 -include $(TOP)/configure/CONFIG_SITE.Common.$(T_A)
 -include $(TOP)/configure/CONFIG_SITE.$(EPICS_HOST_ARCH).$(T_A)
endif

CFG += CONFIG_REQ

include $(TOP)/configure/RULES

distclean: realclean cvsclean realuninstall

CVSCLEAN = $(call FIND_TOOL,cvsclean.pl)
cvsclean:
	$(PERL) $(CVSCLEAN)

realuninstall: uninstallDirs
	$(RMDIR) $(INSTALL_LOCATION_BIN)
	$(RMDIR) $(INSTALL_LOCATION_LIB)

UNINSTALL_DIRS += $(INSTALL_DBD) $(INSTALL_INCLUDE) $(INSTALL_DOC) \
    $(INSTALL_HTML) $(INSTALL_TEMPLATES) $(INSTALL_DB) $(DIRECTORY_TARGETS)
uninstallDirs:
	$(RMDIR) $(UNINSTALL_DIRS)
