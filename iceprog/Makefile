# CC = clang
LDLIBS = -lftdi -lm
CFLAGS = -MD -O0 -ggdb -Wall -std=c99

all: iceprog

iceprog: iceprog.o

install: all
	cp iceprog /usr/local/bin/iceprog

uninstall:
	rm -f /usr/local/bin/iceprog

clean:
	rm -f iceprog
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

