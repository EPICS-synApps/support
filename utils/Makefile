#FILENAME:	Makefile
#USAGE:		Top Makefile
#Version:	$Revision: 1.6 $
#Modified By:	$Author: sluiter $
#Last Modified:	$Date: 2001-11-05 20:42:57 $
#NOTE..	The "DIRS" order is based on compile time dependencies.
#	The user must modify SUPPORT for local configuration.

SUPPORT = !!Set to <supporttop> complete pathname!!

include $(SUPPORT)/config/RELEASE
include $(EPICS_BASE)/config/CONFIG_COMMON

#include $(SUPPORT)/config/ALLEN_BRADLEY_RELEASE
#DIRS += $(ALLEN_BRADLEY)
#RELEASE_FILES += $(ALLEN_BRADLEY)/config/RELEASE
#MASTER_FILES  += $(SUPPORT)/config/ALLEN_BRADLEY_RELEASE

include $(SUPPORT)/config/BITBUS_RELEASE
DIRS += $(BITBUS)
RELEASE_FILES += $(BITBUS)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/BITBUS_RELEASE

include $(SUPPORT)/config/IPAC_RELEASE
DIRS += $(IPAC)
RELEASE_FILES += $(IPAC)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/IPAC_RELEASE

include $(SUPPORT)/config/MPF_RELEASE
DIRS += $(MPF)
RELEASE_FILES += $(MPF)/config/RELEASE
MASTER_FILES +=  $(SUPPORT)/config/MPF_RELEASE

include $(SUPPORT)/config/MPFGPIB_RELEASE
DIRS += $(MPF_GPIB)
RELEASE_FILES += $(MPF_GPIB)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/MPFGPIB_RELEASE

include $(SUPPORT)/config/MPFSERIAL_RELEASE
DIRS += $(MPF_SERIAL)
RELEASE_FILES += $(MPF_SERIAL)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/MPFSERIAL_RELEASE

include $(SUPPORT)/config/MOTOR_RELEASE
DIRS += $(MOTOR)
RELEASE_FILES += $(MOTOR)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/MOTOR_RELEASE

include $(SUPPORT)/config/STD_RELEASE
DIRS += $(STD)
RELEASE_FILES += $(STD)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/STD_RELEASE

include $(SUPPORT)/config/DAC128V_RELEASE
DIRS += $(DAC128V)
RELEASE_FILES += $(DAC128V)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/DAC128V_RELEASE

include $(SUPPORT)/config/IPUNIDIG_RELEASE
DIRS += $(IPUNIDIG)
RELEASE_FILES += $(IPUNIDIG)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/IPUNIDIG_RELEASE

include $(SUPPORT)/config/LOVE_RELEASE
DIRS += $(LOVE)
RELEASE_FILES += $(LOVE)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/LOVE_RELEASE

include $(SUPPORT)/config/MCA_RELEASE
DIRS += $(MCA)
RELEASE_FILES += $(MCA)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/MCA_RELEASE

include $(SUPPORT)/config/CAMAC_RELEASE
DIRS += $(CAMAC)
RELEASE_FILES += $(CAMAC)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/CAMAC_RELEASE

include $(SUPPORT)/config/IP330_RELEASE
DIRS += $(IP330)
RELEASE_FILES += $(IP330)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/IP330_RELEASE

include $(SUPPORT)/config/IP_RELEASE
DIRS += $(IP)
RELEASE_FILES += $(IP)/config/RELEASE
MASTER_FILES  += $(SUPPORT)/config/IP_RELEASE

DIRS += $(SUPPORT)/xxx
RELEASE_FILES += $(SUPPORT)/xxx/config/RELEASE

all install clean rebuild inc depends build uninstall::
	@$(PERL) makeReleaseConsistent.pl $(SUPPORT) $(EPICS_BASE) $(MASTER_FILES) $(RELEASE_FILES)

include $(SUPPORT)/config/RULES_DIRS
