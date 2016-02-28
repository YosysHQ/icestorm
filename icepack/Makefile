include ../config.mk
ifeq ($(STATIC), 1)
LDLIBS = -static -static-libgcc -lm -lstdc++
CXXFLAGS = -MD -O0 -Wall -std=c++11 -I/usr/local/include
else
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11 -I/usr/local/include
endif
MXEGCC = /usr/local/src/mxe/usr/bin/i686-pc-mingw32-gcc

all: icepack$(EXE) iceunpack$(EXE)

icepack$(EXE): icepack.o
	$(CC) -o $@ $(LDFLAGS) $^ $(LDLIBS)

iceunpack: icepack
	ln -sf icepack iceunpack

iceunpack.exe:
	# no iceunpack.exe, use icepack -u

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icepack $(DESTDIR)$(PREFIX)/bin/icepack
	ln -sf icepack $(DESTDIR)$(PREFIX)/bin/iceunpack

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icepack
	rm -f $(DESTDIR)$(PREFIX)/bin/iceunpack

clean:
	rm -f icepack
	rm -f iceunpack
	rm -f icepack.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean
