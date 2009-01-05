OSTYPE := $(shell uname -s)

ifeq ($(OSTYPE),SunOS)
  EXT_LIB=-lnsl
else
  EXT_LIB=
endif

CC = gcc
AR = ar
CFLAGS = -Wall -O2

TARGETS = mda-dump mda-info mda2ascii libmda-load.a


all: $(TARGETS)

mda-dump: mda_dump.o mda_loader.o mda-load.h
	$(CC) mda_dump.o mda_loader.o -o mda-dump $(EXT_LIB)

mda-info: mda_info.c
	$(CC) mda_info.c -o mda-info $(EXT_LIB)

mda2ascii: mda_ascii.o mda_loader.o mda-load.h
	$(CC) mda_ascii.o mda_loader.o -o mda2ascii $(EXT_LIB)

libmda-load.a: mda-load.h mda_loader.o
	$(AR) rcs libmda-load.a mda_loader.o

mda_loader.o: mda-load.h
mda_dump.o:   mda-load.h
mda_ascii.o:  mda-load.h


.PHONY : doc
doc: mda2ascii.1 mda-dump.1 mda-info.1
	groff -man -Tps mda2ascii.1 > mda2ascii.ps
	groff -man -Thtml mda2ascii.1 > mda2ascii.html
	ps2pdf mda2ascii.ps
	groff -man -Tps mda-dump.1 > mda-dump.ps
	groff -man -Thtml mda-dump.1 > mda-dump.html
	ps2pdf mda-dump.ps
	groff -man -Tps mda-info.1 > mda-info.ps
	groff -man -Thtml mda-info.1 > mda-info.html
	ps2pdf mda-info.ps


.PHONY : clean
clean:
	-rm *.o $(TARGETS)

