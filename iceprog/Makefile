include ../config.mk

ifneq ($(shell uname -s),Darwin)
  LDLIBS = -L/usr/local/lib -lm
else
  LIBFTDI_NAME = $(shell $(PKG_CONFIG) --exists libftdi1 && echo ftdi1 || echo ftdi)
  LDLIBS = -L/usr/local/lib -l$(LIBFTDI_NAME) -lm
endif

ifeq ($(STATIC),1)
LDFLAGS += -static
LDLIBS += $(shell for pkg in libftdi1 libftdi; do $(PKG_CONFIG) --silence-errors --static --libs $$pkg && exit; done; echo -lftdi; )
CFLAGS += $(shell for pkg in libftdi1 libftdi; do $(PKG_CONFIG) --silence-errors --static --cflags $$pkg && exit; done; )
else
LDLIBS += $(shell for pkg in libftdi1 libftdi; do $(PKG_CONFIG) --silence-errors --libs $$pkg && exit; done; echo -lftdi; )
CFLAGS += $(shell for pkg in libftdi1 libftdi; do $(PKG_CONFIG) --silence-errors --cflags $$pkg && exit; done; )
endif

all: $(PROGRAM_PREFIX)iceprog$(EXE)

$(PROGRAM_PREFIX)iceprog$(EXE): iceprog.o mpsse.o
	$(CC) -o $@ $(LDFLAGS) $^ $(LDLIBS)

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp $(PROGRAM_PREFIX)iceprog$(EXE) $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)iceprog$(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)iceprog$(EXE)

clean:
	rm -f $(PROGRAM_PREFIX)iceprog
	rm -f $(PROGRAM_PREFIX)iceprog.exe
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

