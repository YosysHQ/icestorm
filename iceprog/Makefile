# CC = clang
LDLIBS = -lftdi -lm
CFLAGS = -MD -O0 -ggdb -Wall -std=c99
DESTDIR = /usr/local

all: iceprog

iceprog: iceprog.o

install: all
	cp iceprog $(DESTDIR)/bin/iceprog

uninstall:
	rm -f $(DESTDIR)/bin/iceprog

clean:
	rm -f iceprog
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

