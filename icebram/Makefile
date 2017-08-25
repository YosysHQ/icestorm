include ../config.mk

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icebram$(EXE)

icebram$(EXE): icebram.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

check: all
	bash rundemo.sh

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icebram$(EXE) $(DESTDIR)$(PREFIX)/bin/icebram$(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icebram$(EXE)

clean:
	rm -f icebram
	rm -f icebram.exe
	rm -f demo.* demo_*.*
	rm -f *.o *.d

-include *.d

.PHONY: all check install uninstall clean

