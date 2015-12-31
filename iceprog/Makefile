include ../config.mk
LDLIBS = -L/usr/local/lib -lftdi -lm
CFLAGS = -MD -O0 -ggdb -Wall -std=c99 -I/usr/local/include
MXEGCC = /usr/local/src/mxe/usr/bin/i686-pc-mingw32-gcc

all: iceprog

iceprog: iceprog.o

iceprog.exe: iceprog.c
	$(MXEGCC) -std=c99 -o iceprog.exe -Os iceprog.c -lftdi -lusb -lm

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp iceprog $(DESTDIR)$(PREFIX)/bin/iceprog

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/iceprog

clean:
	rm -f iceprog
	rm -f iceprog.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

