OSTYPE := $(shell uname -s)

ifeq ($(OSTYPE),SunOS)
  EXT_LIB=-lnsl
else
  EXT_LIB=
endif

CC = gcc
AR = ar
CFLAGS = -Wall -O2
#CFLAGS = -Wall -O2 -g

TARGETS = libmda-load.a mda2ascii mda-dump mda-info mda-ls 


all: $(TARGETS)

libmda-load.a: mda-load.h mda_loader.o
	$(AR) rcs libmda-load.a mda_loader.o

mda2ascii: mda_ascii.o mda_loader.o mda-load.h
	$(CC) mda_ascii.o mda_loader.o -o mda2ascii $(EXT_LIB)

mda-dump: mda_dump.o
	$(CC) mda_dump.o -o mda-dump $(EXT_LIB)

mda-info: mda_info.o mda_loader.o mda-load.h
	$(CC) mda_info.o mda_loader.o -o mda-info $(EXT_LIB)

mda-ls: mda_ls.o mda_loader.o mda-load.h
	$(CC) mda_ls.o mda_loader.o -o mda-ls $(EXT_LIB)


mda_loader.o: mda-load.h
mda_ascii.o:  mda-load.h
mda_dump.o:
mda_info.o:   mda-load.h
mda_ls.o:     mda-load.h


.PHONY : clean
clean:
	-rm *.o $(TARGETS)


prefix = /usr/local
bindir = $(prefix)/bin
mandir = $(prefix)/man
includedir = $(prefix)/include
libdir = $(prefix)/lib

install : all
	-mkdir -p $(bindir)
	-mkdir -p $(mandir)
	-mkdir -p $(includedir)
	-mkdir -p $(libdir)
	cp mda-ls $(bindir)/
	cp mda-info $(bindir)/
	cp mda-dump $(bindir)/
	cp mda2ascii $(bindir)/
	cp libmda-load.a $(libdir)/
	cp mda-load.h $(includedir)/
	cp documentation/mda-ls.1 $(mandir)/man1/
	cp documentation/mda-info.1 $(mandir)/man1/
	cp documentation/mda-dump.1 $(mandir)/man1/
	cp documentation/mda2ascii.1 $(mandir)/man1/

