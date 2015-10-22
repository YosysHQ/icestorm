# CXX = clang
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11 -I/usr/local/include
CC = $(CXX)
DESTDIR = /usr/local

all: icetime

icetime: icetime.o

install: all
	cp icetime $(DESTDIR)/bin/icetime

uninstall:
	rm -f $(DESTDIR)/bin/icetime


# View timing netlist:
#  yosys -qp 'read_verilog -lib cells.v; prep; show' test0_ref.v

test0 test1 test2 test3 test4 test5 test6 test7 test8 test9: icetime
	python3 mktest.py $@
	./icetime -P tq144 -p $@.pcf $@.txt $@_out.v
	yosys $@.ys

mktest: test0 test1 test2 test3 test4 test5 test6 test7 test8 test9

clean:
	rm -f icetime
	rm -f test[0-9]*
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

