include ../config.mk

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icemulti$(EXE)

icemulti$(EXE): icemulti.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

check: all
	cd tests; ./run-tests

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icemulti$(EXE) $(DESTDIR)$(PREFIX)/bin/icemulti$(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icemulti$(EXE)

clean:
	rm -f icemulti
	rm -f icemulti.exe
	rm -f *.o *.d

-include *.d

.PHONY: all check install uninstall clean

