include ../config.mk

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: $(PROGRAM_PREFIX)icepll$(EXE)

$(PROGRAM_PREFIX)icepll$(EXE): icepll.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp $(PROGRAM_PREFIX)icepll$(EXE) $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icepll$(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icepll$(EXE)

clean:
	rm -f $(PROGRAM_PREFIX)icepll$(EXE)
	rm -f $(PROGRAM_PREFIX)icepll.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

