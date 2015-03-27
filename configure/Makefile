TOP=..

include $(TOP)/configure/CONFIG

TARGETS = $(CONFIG_TARGETS)
CONFIGS += $(subst ../,,$(wildcard $(CONFIG_INSTALLS)))
CHECK_RELEASE = YES

include $(TOP)/configure/RULES

# Configure is not a top-level directory, but it seems easier for us to pretend
# that it is than to figure out how to make support/Makefile fan out commands
# to directories some of which are top-level and some of which are not.
# We want support/Makefile to build configure, so we get CHECK_RELEASE, and we
# want to be able to do commands like "make uninstall.<arch>" in support.
# The following rules are modelled on stuff in base/configure/RULES_TOP.

uninstall realuninstall:
	@echo "\c"

distclean: realclean

uninstallArchTargets = $(foreach arch,$(BUILD_ARCHS), uninstall$(DIVIDER)$(arch))

$(uninstallArchTargets):
	@echo "\c"
