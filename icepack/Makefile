# CXX = clang
CXX ?= clang
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11 -I/usr/local/include
MXEGCC = /usr/local/src/mxe/usr/bin/i686-pc-mingw32-gcc
CC = $(CXX)
DESTDIR = /usr/local

all: icepack iceunpack

icepack: icepack.o

icepack.exe: icepack.cc
	$(MXEGCC) -std=c++11 -o icepack.exe -Os icepack.cc -lm -lstdc++

iceunpack: icepack
	ln -sf icepack iceunpack

install: all
	cp icepack $(DESTDIR)/bin/icepack
	ln -sf icepack $(DESTDIR)/bin/iceunpack

uninstall:
	rm -f $(DESTDIR)/bin/icepack
	rm -f $(DESTDIR)/bin/iceunpack

clean:
	rm -f icepack
	rm -f iceunpack
	rm -f icepack.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

