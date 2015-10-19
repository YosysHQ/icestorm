# CXX = clang
CXX ?= clang
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11 -I/usr/local/include
CC = $(CXX)
DESTDIR = /usr/local

all: icetime

icetime: icetime.o

install: all
	cp icetime $(DESTDIR)/bin/icetime

uninstall:
	rm -f $(DESTDIR)/bin/icetime

clean:
	rm -f icetime
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

