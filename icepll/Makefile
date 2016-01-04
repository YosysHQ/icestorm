include ../config.mk
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11 -I/usr/local/include

all: icepll

icepll: icepll.o

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icepll $(DESTDIR)$(PREFIX)/bin/icepll

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icepll

clean:
	rm -f icepll *.o *.d

-include *.d

.PHONY: all install uninstall clean

