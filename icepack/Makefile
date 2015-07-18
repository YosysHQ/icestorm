# CXX = clang
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11
CC = $(CXX)

all: icepack iceunpack

icepack: icepack.o

iceunpack: icepack
	ln -sf icepack iceunpack

install: all
	cp icepack /usr/local/bin/icepack
	ln -sf icepack /usr/local/bin/iceunpack

uninstall:
	rm -f /usr/local/bin/icepack
	rm -f /usr/local/bin/iceunpack

clean:
	rm -f icepack
	rm -f iceunpack
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

