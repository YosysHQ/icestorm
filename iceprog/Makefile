include ../config.mk
LDLIBS = -L/usr/local/lib -lm
CFLAGS = -MD -O0 -ggdb -Wall -std=c99 -I/usr/local/include

LDLIBS += $(shell for pkg in libftdi libftdi1; do $(PKG_CONFIG) --silence-errors --libs $$pkg && exit; done; echo -lftdi; )
CFLAGS += $(shell for pkg in libftdi libftdi1; do $(PKG_CONFIG) --silence-errors --cflags $$pkg && exit; done; )

all: iceprog$(EXE)

iceprog$(EXE): iceprog.o
	$(CC) -o $@ $(LDFLAGS) $^ $(LDLIBS)

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp iceprog $(DESTDIR)$(PREFIX)/bin/iceprog

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/iceprog

clean:
	rm -f iceprog
	rm -f iceprog.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

