
all: icecompr iceuncompr

test: example_1k.ok example_8k.ok

icecompr: icecompr.cc
	clang++ -o icecompr -Wall -Wextra -std=c++11 icecompr.cc

iceuncompr: iceuncompr.c
	clang -o iceuncompr -Wall -Wextra iceuncompr.c

%.compr: %.bin icecompr
	./icecompr -v $< $@
	

%.uncompr: %.compr iceuncompr
	./iceuncompr $< $@

%.ok: %.uncompr %.bin
	cmp $^
	touch $@

clean:
	rm -f icecompr iceuncompr *.d
	rm -f example_1k.compr example_8k.compr
	rm -f example_1k.uncompr example_8k.uncompr
	rm -f example_1k.ok example_8k.ok

.SECONDARY:
.PHONY: all test clean

