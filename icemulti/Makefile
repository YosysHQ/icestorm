include ../config.mk

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icemulti$(EXE)

icemulti$(EXE): icemulti.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icemulti $(DESTDIR)$(PREFIX)/bin/icemulti

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icemulti

clean:
	rm -f icemulti
	rm -f icemulti.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

