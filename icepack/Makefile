
CC = clang
CXX = clang
LDFLAGS = -lm -lstdc++
CFLAGS = -MD -Os -Wall -std=c99
CXXFLAGS = -MD -Os -Wall -std=c99

all: iceunpack

iceunpack: iceunpack.o

install: all
	cp iceunpack /usr/local/bin/iceunpack

uninstall:
	rm -f /usr/local/bin/iceunpack

clean:
	rm -f iceunpack
	rm -f *.o *.d

-include *.d

.PHONY: install uninstall clean

