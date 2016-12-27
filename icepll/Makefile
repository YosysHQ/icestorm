include ../config.mk
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11 -I/usr/local/include

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icepll$(EXE)

icepll$(EXE): icepll.o
	$(CC) -o $@ $(LDFLAGS) $^ $(LDLIBS)

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

