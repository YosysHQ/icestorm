include ../config.mk
MXEGCC = /usr/local/src/mxe/usr/bin/i686-pc-mingw32-gcc

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icepack$(EXE) iceunpack$(EXE)

icepack$(EXE): icepack.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

iceunpack: icepack
	ln -sf icepack iceunpack

iceunpack.exe:
	# no iceunpack.exe, use icepack -u

check: all

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icepack$(EXE) $(DESTDIR)$(PREFIX)/bin/icepack$(EXE)
	ln -sf icepack$(EXE) $(DESTDIR)$(PREFIX)/bin/iceunpack$(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icepack$(EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/iceunpack$(EXE)

clean:
	rm -f icepack
	rm -f iceunpack
	rm -f icepack.exe
	rm -f *.o *.d

-include *.d

.PHONY: all check install uninstall clean

