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
#  yosys -qp 'read_verilog -lib cells.v; prep; show' test0_out.v

test0 test1 test2 test3 test4 test5 test6 test7 test8 test9: icetime
	test -f $@_ref.v || python3 mktest.py $@
	./icetime -P tq144 -p $@.pcf $@.txt $@_out.v
	yosys $@.ys

run0 run1 run2 run3 run4 run5 run6 run7 run8 run9: icetime
	./icetime -P tq144 -p $(subst run,test,$@).pcf $(subst run,test,$@).txt $(subst run,test,$@)_out.v

show0 show1 show2 show3 show4 show5 show6 show7 show8 show9:
	yosys -p ':equiv_purge; opt_clean -purge; show' $(subst show,test,$@).il

test: test0 test1 test2 test3 test4 test5 test6 test7 test8 test9

clean:
	rm -f icetime
	rm -f test[0-9]*
	rm -f *.o *.d

-include *.d

.PHONY: all install uninstall clean

