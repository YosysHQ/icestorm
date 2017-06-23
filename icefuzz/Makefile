include ../config.mk
export LC_ALL=C
export ICE_SBTIMER_LP=1

DEVICECLASS := 1k

ifeq ($(DEVICECLASS), 384)
  DEVICE := lp384-cm49
	THREEH = _384
endif

ifeq ($(DEVICECLASS), 1k)
	DEVICE := hx1k-tq144
endif

ifeq ($(DEVICECLASS), 5k)
  DEVICE := up5k-sg48
	RAM_SUFFIX := _5k
endif

ifeq ($(DEVICECLASS), 8k)
  DEVICE := hx8k-ct256
  RAM_SUFFIX = _8k
endif

TESTS =
TESTS += binop
TESTS += pin2pin
TESTS += mesh
TESTS += fanout
TESTS += logic
TESTS += cluster
TESTS += iopack
TESTS += io
TESTS += gbio
TESTS += gbio2
TESTS += prim
TESTS += fflogic
ifneq ($(DEVICECLASS),384)
 TESTS += ram40
 TESTS += mem
 TESTS += pll
 TESTS += aig
endif

database: bitdata_io.txt bitdata_logic.txt bitdata_ramb$(RAM_SUFFIX).txt bitdata_ramt$(RAM_SUFFIX).txt
ifneq ($(RAM_SUFFIX),)
	cp cached_ramb.txt bitdata_ramb.txt
	cp cached_ramt.txt bitdata_ramt.txt
else
	cp cached_ramb$(RAM_SUFFIX).txt bitdata_ramb$(RAM_SUFFIX).txt
	cp cached_ramt$(RAM_SUFFIX).txt bitdata_ramt$(RAM_SUFFIX).txt
endif
	ICEDEVICE=$(DEVICECLASS) python3 database.py
	python3 export.py
	diff -U0 cached_io.txt bitdata_io.txt || cp -v bitdata_io.txt cached_io.txt
	diff -U0 cached_logic.txt bitdata_logic.txt || cp -v bitdata_logic.txt cached_logic.txt
	diff -U0 cached_ramb$(RAM_SUFFIX).txt bitdata_ramb$(RAM_SUFFIX).txt || cp -v bitdata_ramb$(RAM_SUFFIX).txt cached_ramb$(RAM_SUFFIX).txt
	diff -U0 cached_ramt$(RAM_SUFFIX).txt bitdata_ramt$(RAM_SUFFIX).txt || cp -v bitdata_ramt$(RAM_SUFFIX).txt cached_ramt$(RAM_SUFFIX).txt

timings:
ifeq ($(DEVICECLASS),8k)
	cp tmedges.txt tmedges.tmp
	set -e; for f in work_*/*.vsb; do echo $$f; yosys -q -f verilog -s tmedges.ys $$f; done
	sort -u tmedges.tmp > tmedges.txt && rm -f tmedges.tmp
	python3 timings.py -t timings_hx8k.txt work_*/*.sdf > timings_hx8k.new
	mv timings_hx8k.new timings_hx8k.txt
	python3 timings.py -t timings_lp8k.txt work_*/*.slp > timings_lp8k.new
	mv timings_lp8k.new timings_lp8k.txt
else
 ifeq ($(DEVICECLASS),384)
	cp tmedges.txt tmedges.tmp
	set -e; for f in work_*/*.vsb; do echo $$f; yosys -q -f verilog -s tmedges.ys $$f; done
	sort -u tmedges.tmp > tmedges.txt && rm -f tmedges.tmp
	python3 timings.py -t timings_lp384.txt work_*/*.slp > timings_lp384.new
	mv timings_lp384.new timings_lp384.txt
 else
	cp tmedges.txt tmedges.tmp
	set -e; for f in work_*/*.vsb; do echo $$f; yosys -q -f verilog -s tmedges.ys $$f; done
	sort -u tmedges.tmp > tmedges.txt && rm -f tmedges.tmp
	python3 timings.py -t timings_hx1k.txt work_*/*.sdf > timings_hx1k.new
	mv timings_hx1k.new timings_hx1k.txt
	python3 timings.py -t timings_lp1k.txt work_*/*.slp > timings_lp1k.new
	mv timings_lp1k.new timings_lp1k.txt
 endif
endif

timings_html:
	python3 timings.py -h tmedges.txt -t timings_hx1k.txt -l "HX1K with default temp/volt settings" > timings_hx1k.html
	python3 timings.py -h tmedges.txt -t timings_hx8k.txt -l "HX8K with default temp/volt settings" > timings_hx8k.html
	python3 timings.py -h tmedges.txt -t timings_lp1k.txt -l "LP1K with default temp/volt settings" > timings_lp1k.html
	python3 timings.py -h tmedges.txt -t timings_lp8k.txt -l "LP8K with default temp/volt settings" > timings_lp8k.html
	python3 timings.py -h tmedges.txt -t timings_lp384.txt -l "LP384 with default temp/volt settings" > timings_lp384.html

data_cached.txt: cached_io.txt cached_logic.txt cached_ramb$(RAM_SUFFIX).txt cached_ramt$(RAM_SUFFIX).txt
	gawk '{ print "io", $$0; }' cached_io.txt > data_cached.new
	gawk '{ print "logic", $$0; }' cached_logic.txt >> data_cached.new
	gawk '{ print "ramb$(RAM_SUFFIX)", $$0; }' cached_ramb$(RAM_SUFFIX).txt >> data_cached.new
	gawk '{ print "ramt$(RAM_SUFFIX)", $$0; }' cached_ramt$(RAM_SUFFIX).txt >> data_cached.new
	mv data_cached.new data_cached.txt

bitdata_io.txt: data_cached.txt $(addprefix data_,$(addsuffix .txt,$(TESTS)))
	grep ^io $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

bitdata_logic.txt: data_cached.txt $(addprefix data_,$(addsuffix .txt,$(TESTS)))
	grep ^logic $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

bitdata_ramb$(RAM_SUFFIX).txt: data_cached.txt $(addprefix data_,$(addsuffix .txt,$(TESTS)))
	grep ^ramb$(RAM_SUFFIX) $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

bitdata_ramt$(RAM_SUFFIX).txt: data_cached.txt $(addprefix data_,$(addsuffix .txt,$(TESTS)))
	grep ^ramt$(RAM_SUFFIX) $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

datafiles: $(addprefix data_,$(addsuffix .txt,$(TESTS)))

../icepack/icepack:
	$(MAKE) -C ../icepack

define data_template
data_$(1).txt: make_$(1).py ../icepack/icepack
	ICEDEVICE=$(DEVICECLASS) python3 make_$(1).py
	+ICEDEV=$(DEVICE) $(MAKE) -C work_$(1)
	ICEDEVICE=$(DEVICECLASS) python3 extract.py work_$(1)/*.glb > $$@
endef

$(foreach test,$(TESTS),$(eval $(call data_template,$(test))))

%.ok: %.bin
	bash check.sh $<

check: $(addsuffix .ok,$(basename $(wildcard work_binop/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_pin2pin/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_mesh/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_fanout/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_logic/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_cluster/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_iopack/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_pll/*.bin)))

clean:
	rm -rf work_*
	rm -rf data_*.txt
	rm -rf bitdata_*.txt
	rm -rf database_*.txt
	rm -rf timings_*.html

.PHONY: database datafiles check clean
