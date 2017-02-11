include ../config.mk

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icebram$(EXE)

icebram$(EXE): icebram.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

test: icebram
	bash rundemo.sh

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icebram $(DESTDIR)$(PREFIX)/bin/icebram

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icebram

clean:
	rm -f icebram
	rm -f icebram.exe
	rm -f demo.* demo_*.*
	rm -f *.o *.d

-include *.d

.PHONY: all test install uninstall clean

