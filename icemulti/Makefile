include ../config.mk

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: $(PROGRAM_PREFIX)icemulti$(EXE)

$(PROGRAM_PREFIX)icemulti$(EXE): icemulti.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp $(PROGRAM_PREFIX)icemulti$(EXE) $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icemulti$(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icemulti$(EXE)

clean:
	rm -f $(PROGRAM_PREFIX)icemulti$(EXE)
	rm -f $(PROGRAM_PREFIX)icemulti.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

