include ../config.mk

all: icecompr iceuncompr

test: example_1k.ok example_8k.ok

icecompr: icecompr.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

iceuncompr: iceuncompr.o
	$(CC) -o $@ $(LDFLAGS) $^ $(LDLIBS)

%.compr: %.bin icecompr
	./icecompr -v $< $@

%.compr_py: %.bin icecompr.py
	./icecompr.py < $< > $@

%.uncompr: %.compr iceuncompr
	./iceuncompr $< $@

%.ok: %.compr %.compr_py %.uncompr %.bin
	cmp $(basename $@).compr $(basename $@).compr_py
	cmp $(basename $@).uncompr $(basename $@).bin
	touch $@

clean:
	rm -f icecompr iceuncompr *.d
	rm -f example_1k.compr example_8k.compr
	rm -f example_1k.compr_py example_8k.compr_py
	rm -f example_1k.uncompr example_8k.uncompr
	rm -f example_1k.ok example_8k.ok

.SECONDARY:
.PHONY: all test clean

