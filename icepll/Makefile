include ../config.mk

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icepll$(EXE)

icepll$(EXE): icepll.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

check: all

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icepll$(EXE) $(DESTDIR)$(PREFIX)/bin/icepll$(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icepll$(EXE)

clean:
	rm -f icepll
	rm -f icepll.exe
	rm -f *.o *.d

-include *.d

.PHONY: all check install uninstall clean

