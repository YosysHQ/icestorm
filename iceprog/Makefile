include ../config.mk
LDLIBS = -L/usr/local/lib -lftdi -lm
CFLAGS = -MD -O0 -ggdb -Wall -std=c99 -I/usr/local/include

ifeq ($(MXE),1)
LDLIBS += -lusb
endif

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

