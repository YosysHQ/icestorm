include ../config.mk
LDLIBS = -lm -lstdc++
override CXXFLAGS += -DPREFIX='"$(PREFIX)"' -DCHIPDB_SUBDIR='"$(CHIPDB_SUBDIR)"'

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icetime$(EXE)

icetime$(EXE): icetime.o
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

icetime.o: icetime.cc timings.inc

timings.inc: timings.py ../icefuzz/timings_*.txt
	python3 timings.py > timings.inc.new
	mv timings.inc.new timings.inc

check: all

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp icetime$(EXE) $(DESTDIR)$(PREFIX)/bin/icetime$(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icetime$(EXE)


# View timing netlist:
#  yosys -qp 'read_verilog -lib cells.v; prep; show' test0_ref.v
#  yosys -qp 'read_verilog -lib cells.v; prep; show' test0_out.v

test0 test1 test2 test3 test4 test5 test6 test7 test8 test9: icetime
	test -f $@_ref.v || python3 mktest.py $@
	./icetime -m -d hx1k -P tq144 -p $@.pcf -o $@_out.v $@.asc
	yosys $@.ys

run0 run1 run2 run3 run4 run5 run6 run7 run8 run9: icetime
	./icetime -t -d hx1k -P tq144 -p $(subst run,test,$@).pcf $(subst run,test,$@).asc

show0 show1 show2 show3 show4 show5 show6 show7 show8 show9: icetime
	bash show.sh $(subst show,test,$@)
	xdot $(subst show,test,$@).dot

test: test0 test1 test2 test3 test4 test5 test6 test7 test8 test9

show: show0 show1 show2 show3 show4 show5 show6 show7 show8 show9

clean:
	rm -f icetime icetime.exe timings.inc *.o *.d
	rm -rf test[0-9]*

-include *.d

.PHONY: all check install uninstall clean

