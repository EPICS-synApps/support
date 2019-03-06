
TARGETS = libmda-load.a mda2ascii mda-dump mda-info mda-ls 

all: $(TARGETS)

libmda-load.a: mda-load.h mda_loader.o $(MORE_OBJS)
	$(AR) rcs libmda-load.a mda_loader.o $(MORE_OBJS)

mda2ascii: mda_ascii.o libmda-load.a mda-load.h
	$(CC) mda_ascii.o libmda-load.a -o mda2ascii

mda-dump: mda_dump.o $(MORE_OBJS)
	$(CC) mda_dump.o -o mda-dump $(MORE_OBJS)

mda-info: mda_info.o libmda-load.a mda-load.h
	$(CC) mda_info.o libmda-load.a -o mda-info

mda-ls: mda_ls.o libmda-load.a mda-load.h
	$(CC) mda_ls.o libmda-load.a -o mda-ls


mda_dump.o:
mda_loader.o: mda-load.h
mda_ascii.o:  mda-load.h
mda_info.o:   mda-load.h
mda_ls.o:     mda-load.h
xdr_hack.o:   xdr_hack.h


.PHONY : clean
clean:
	-rm *.o $(TARGETS)


