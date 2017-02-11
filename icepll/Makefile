include ../config.mk

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icepll$(EXE)

icepll$(EXE): icepll.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icepll $(DESTDIR)$(PREFIX)/bin/icepll

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icepll

clean:
	rm -f icepll
	rm -f icepll.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

