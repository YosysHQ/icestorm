# CC = clang
LDLIBS = -L/usr/local/lib -lftdi -lm -L/opt/local/lib
CFLAGS = -MD -O0 -ggdb -Wall -std=c99 -I/usr/local/include -I/opt/local/include
MXEGCC = /usr/local/src/mxe/usr/bin/i686-pc-mingw32-gcc
DESTDIR = /usr/local

all: iceprog

iceprog: iceprog.o

iceprog.exe: iceprog.c
	$(MXEGCC) -std=c99 -o iceprog.exe -Os iceprog.c -lftdi -lusb -lm

install: all
	cp iceprog $(DESTDIR)/bin/iceprog

uninstall:
	rm -f $(DESTDIR)/bin/iceprog

clean:
	rm -f iceprog
	rm -f iceprog.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

