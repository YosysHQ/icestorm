include ../config.mk
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -Wextra -std=c++11

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icecompr$(EXE) iceuncompr$(EXE)

icecompr$(EXE): icecompr.cc
	$(CXX) $(CXXFLAGS) -o $@ $(LDFLAGS) $^ $(LDLIBS)

iceuncompr$(EXE): iceuncompr.c libiceuncompr.c
	$(CC) -o $@ $(LDFLAGS) $< $(LDLIBS)

test: example_1k.ok example_8k.ok

%.compr: %.bin icecompr$(EXE)
	./icecompr$(EXE) -v $< $@

%.uncompr: %.compr iceuncompr$(EXE)
	./iceuncompr$(EXE) $< $@

%.ok: %.uncompr %.bin
	cmp $^
	touch $@

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin $(DESTDIR)$(PREFIX)/share/icecompr
	cp icecompr$(EXE) $(DESTDIR)$(PREFIX)/bin/icecompr$(EXE)
	cp iceuncompr$(EXE) $(DESTDIR)$(PREFIX)/bin/iceuncompr$(EXE)
	cp libiceuncompr.c $(DESTDIR)$(PREFIX)/share/icecompr/libiceuncompr.c

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icecompr$(EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/iceuncompr$(EXE)

clean:
	rm -f icecompr$(EXE) iceuncompr$(EXE)
	rm -f example_1k.compr example_8k.compr
	rm -f example_1k.uncompr example_8k.uncompr
	rm -f example_1k.ok example_8k.ok

.PHONY: all test install uninstall clean
