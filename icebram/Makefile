include ../config.mk

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: $(PROGRAM_PREFIX)icebram$(EXE)

$(PROGRAM_PREFIX)icebram$(EXE): icebram.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

test: $(PROGRAM_PREFIX)icebram
	bash rundemo.sh

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp $(PROGRAM_PREFIX)icebram$(EXE) $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebram$(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebram$(EXE)

clean:
	rm -f $(PROGRAM_PREFIX)icebram$(EXE)
	rm -f $(PROGRAM_PREFIX)icebram.exe
	rm -f demo.* demo_*.*
	rm -f *.o *.d

-include *.d

.PHONY: all test install uninstall clean

