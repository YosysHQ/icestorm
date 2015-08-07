# CXX = clang
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11
CC = $(CXX)
DESTDIR = /usr/local

all: icemulti

icemulti: icemulti.o

install: all
	cp icemulti $(DESTDIR)/bin/icemulti

uninstall:
	rm -f $(DESTDIR)/bin/icemulti

clean:
	rm -f icemulti
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

