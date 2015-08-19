# CXX = clang
CXX ?= clang
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11 -I/usr/local/include
CC = $(CXX)
DESTDIR = /usr/local

all: icepack iceunpack

icepack: icepack.o

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
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

