include ../config.mk
LDLIBS = -lm -lstdc++
CXXFLAGS = -MD -O0 -ggdb -Wall -std=c++11 -I/usr/local/include

all: icetime

icetime: icetime.o

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icetime $(DESTDIR)$(PREFIX)/bin/icetime

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icetime


# View timing netlist:
#  yosys -qp 'read_verilog -lib cells.v; prep; show' test0_ref.v
#  yosys -qp 'read_verilog -lib cells.v; prep; show' test0_out.v

test0 test1 test2 test3 test4 test5 test6 test7 test8 test9: icetime
	test -f $@_ref.v || python3 mktest.py $@
	./icetime -P tq144 -p $@.pcf $@.asc $@_out.v
	yosys $@.ys

run0 run1 run2 run3 run4 run5 run6 run7 run8 run9: icetime
	./icetime -P tq144 -p $(subst run,test,$@).pcf $(subst run,test,$@).asc $(subst run,test,$@)_out.v

show0 show1 show2 show3 show4 show5 show6 show7 show8 show9: icetime
	bash show.sh $(subst show,test,$@)
	xdot $(subst show,test,$@).dot

test: test0 test1 test2 test3 test4 test5 test6 test7 test8 test9

show: show0 show1 show2 show3 show4 show5 show6 show7 show8 show9

clean:
	rm -f icetime *.o *.d
	rm -rf test[0-9]*

-include *.d

.PHONY: all install uninstall clean

