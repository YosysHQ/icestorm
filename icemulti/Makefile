include ../config.mk
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11

all: icemulti

icemulti: icemulti.o

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icemulti $(DESTDIR)$(PREFIX)/bin/icemulti

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icemulti

clean:
	rm -f icemulti
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

