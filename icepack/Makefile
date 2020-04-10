include ../config.mk
MXEGCC = /usr/local/src/mxe/usr/bin/i686-pc-mingw32-gcc

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: $(PROGRAM_PREFIX)icepack$(EXE) $(PROGRAM_PREFIX)iceunpack$(EXE)

$(PROGRAM_PREFIX)icepack$(EXE): icepack.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

$(PROGRAM_PREFIX)iceunpack$(EXE): $(PROGRAM_PREFIX)icepack$(EXE)
	ln -sf $(PROGRAM_PREFIX)icepack$(EXE) $(PROGRAM_PREFIX)iceunpack$(EXE)

$(PROGRAM_PREFIX)iceunpack.exe:
	# no iceunpack.exe, use icepack -u

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp $(PROGRAM_PREFIX)icepack$(EXE) $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icepack$(EXE)
	ln -sf $(PROGRAM_PREFIX)icepack$(EXE) $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)iceunpack$(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icepack$(EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)iceunpack$(EXE)

clean:
	rm -f $(PROGRAM_PREFIX)icepack$(EXE)
	rm -f $(PROGRAM_PREFIX)iceunpack$(EXE)
	rm -f $(PROGRAM_PREFIX)icepack.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

