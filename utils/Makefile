#FILENAME:	Makefile
#USAGE:		Top Makefile
#Version:	$Revision: 1.5 $
#Modified By:	$Author: sluiter $
#Last Modified:	$Date: 2001-11-02 22:00:10 $
#NOTE..	The "DIRS" order is based on compile time dependencies.
#	The user must modify TOP for local configuration.

TOP = /home/oxygen/SLUITER/ioc_Vx_5-4/support

include $(TOP)/config/RELEASE
include $(EPICS_BASE)/config/CONFIG_COMMON

#include $(TOP)/config/ALLEN_BRADLEY_RELEASE
#DIRS += $(ALLEN_BRADLEY)
#RELEASE_FILES += $(ALLEN_BRADLEY)/config/RELEASE
#MASTER_FILES  += $(TOP)/config/ALLEN_BRADLEY_RELEASE

include $(TOP)/config/BITBUS_RELEASE
DIRS += $(BITBUS)
RELEASE_FILES += $(BITBUS)/config/RELEASE
MASTER_FILES  += $(TOP)/config/BITBUS_RELEASE

include $(TOP)/config/IPAC_RELEASE
DIRS += $(IPAC)
RELEASE_FILES += $(IPAC)/config/RELEASE
MASTER_FILES  += $(TOP)/config/IPAC_RELEASE

include $(TOP)/config/MPF_RELEASE
DIRS += $(MPF)
RELEASE_FILES += $(MPF)/config/RELEASE
MASTER_FILES +=  $(TOP)/config/MPF_RELEASE

include $(TOP)/config/MPFGPIB_RELEASE
DIRS += $(MPF_GPIB)
RELEASE_FILES += $(MPF_GPIB)/config/RELEASE
MASTER_FILES  += $(TOP)/config/MPFGPIB_RELEASE

include $(TOP)/config/MPFSERIAL_RELEASE
DIRS += $(MPF_SERIAL)
RELEASE_FILES += $(MPF_SERIAL)/config/RELEASE
MASTER_FILES  += $(TOP)/config/MPFSERIAL_RELEASE

include $(TOP)/config/MOTOR_RELEASE
DIRS += $(MOTOR)
RELEASE_FILES += $(MOTOR)/config/RELEASE
MASTER_FILES  += $(TOP)/config/MOTOR_RELEASE

include $(TOP)/config/STD_RELEASE
DIRS += $(STD)
RELEASE_FILES += $(STD)/config/RELEASE
MASTER_FILES  += $(TOP)/config/STD_RELEASE

include $(TOP)/config/DAC128V_RELEASE
DIRS += $(DAC128V)
RELEASE_FILES += $(DAC128V)/config/RELEASE
MASTER_FILES  += $(TOP)/config/DAC128V_RELEASE

include $(TOP)/config/IPUNIDIG_RELEASE
DIRS += $(IPUNIDIG)
RELEASE_FILES += $(IPUNIDIG)/config/RELEASE
MASTER_FILES  += $(TOP)/config/IPUNIDIG_RELEASE

include $(TOP)/config/LOVE_RELEASE
DIRS += $(LOVE)
RELEASE_FILES += $(LOVE)/config/RELEASE
MASTER_FILES  += $(TOP)/config/LOVE_RELEASE

include $(TOP)/config/MCA_RELEASE
DIRS += $(MCA)
RELEASE_FILES += $(MCA)/config/RELEASE
MASTER_FILES  += $(TOP)/config/MCA_RELEASE

include $(TOP)/config/CAMAC_RELEASE
DIRS += $(CAMAC)
RELEASE_FILES += $(CAMAC)/config/RELEASE
MASTER_FILES  += $(TOP)/config/CAMAC_RELEASE

include $(TOP)/config/IP330_RELEASE
DIRS += $(IP330)
RELEASE_FILES += $(IP330)/config/RELEASE
MASTER_FILES  += $(TOP)/config/IP330_RELEASE

include $(TOP)/config/IP_RELEASE
DIRS += $(IP)
RELEASE_FILES += $(IP)/config/RELEASE
MASTER_FILES  += $(TOP)/config/IP_RELEASE

DIRS += $(TOP)/xxx
RELEASE_FILES += $(TOP)/xxx/config/RELEASE

all install clean rebuild inc depends build uninstall::
	@$(PERL) makeReleaseConsistent.pl $(TOP) $(EPICS_BASE) $(MASTER_FILES) $(RELEASE_FILES)

include $(TOP)/config/RULES_DIRS
