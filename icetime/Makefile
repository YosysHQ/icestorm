include ../config.mk
LDLIBS = -lm -lstdc++
override CXXFLAGS += -DPREFIX='"$(PREFIX)"' -DCHIPDB_SUBDIR='"$(CHIPDB_SUBDIR)"'

ifeq ($(STATIC),1)
LDFLAGS += -static
endif

all: icetime$(EXE)

CHIPS=lp384 lp1k lp8k hx1k hx8k up5k

ifeq ($(EXE),.js)
icetime$(EXE): | share/$(CHIPDB_SUBDIR)/chipdb-384.txt share/$(CHIPDB_SUBDIR)/chipdb-1k.txt share/$(CHIPDB_SUBDIR)/chipdb-8k.txt share/$(CHIPDB_SUBDIR)/chipdb-5k.txt

share/$(CHIPDB_SUBDIR)/chipdb-384.txt: ../icebox/chipdb-384.txt
	mkdir -p share/$(CHIPDB_SUBDIR)
	cp $< $@
share/$(CHIPDB_SUBDIR)/chipdb-1k.txt: ../icebox/chipdb-1k.txt
	mkdir -p share/$(CHIPDB_SUBDIR)
	cp $< $@
share/$(CHIPDB_SUBDIR)/chipdb-8k.txt: ../icebox/chipdb-8k.txt
	mkdir -p share/$(CHIPDB_SUBDIR)
	cp $< $@
share/$(CHIPDB_SUBDIR)/chipdb-5k.txt: ../icebox/chipdb-5k.txt
	mkdir -p share/$(CHIPDB_SUBDIR)
	cp $< $@
override LDFLAGS += --embed-file share
endif

icetime$(EXE): icetime.o iceutil.o $(addsuffix .o, $(addprefix timings-, $(CHIPS)))
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

timings-%.cc: timings.py ../icefuzz/timings_%.txt
	python3 timings.py $* > $@

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	mkdir -p $(DESTDIR)$(PREFIX)/share/icebox
	cp icetime$(EXE) $(DESTDIR)$(PREFIX)/bin/icetime$(EXE)
	cp ../icefuzz/timings_*.txt $(DESTDIR)$(PREFIX)/share/icebox/

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
	rm -f icetime$(EXE) icetime.exe *.o *.d timings-*.cc
	rm -rf test[0-9]*

-include *.d

.PHONY: all install uninstall clean

