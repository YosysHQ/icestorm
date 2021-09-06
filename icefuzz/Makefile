include ../config.mk
export LC_ALL=C
export ICE_SBTIMER_LP=1

DEVICECLASS = 1k

ifeq ($(DEVICECLASS), 384)
  DEVICE := lp384-cm49
	THREEH = _384
endif

ifeq ($(DEVICECLASS), 1k)
	DEVICE := hx1k-tq144
endif

ifeq ($(DEVICECLASS), u4k)
	DEVICE := u4k-sg48
	RAM_SUFFIX := _8k
endif

ifeq ($(DEVICECLASS), 5k)
	DEVICE := up5k-sg48
	RAM_SUFFIX := _8k
endif

ifeq ($(DEVICECLASS), 4k)
	DEVICE := lm4k-cm49
	RAM_SUFFIX := _8k
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
ifeq ($(DEVICECLASS),5k)
 TESTS += dsp
 TESTS += upip
endif
ifeq ($(DEVICECLASS),u4k)
 TESTS += dsp
 TESTS += uip
endif
database: bitdata_io.txt bitdata_logic.txt bitdata_ramb$(RAM_SUFFIX).txt bitdata_ramt$(RAM_SUFFIX).txt bitdata_dsp0_5k.txt bitdata_dsp1_5k.txt bitdata_dsp2_5k.txt bitdata_dsp3_5k.txt bitdata_ipcon_5k.txt
ifneq ($(RAM_SUFFIX),)
	cp cached_ramb.txt bitdata_ramb.txt
	cp cached_ramt.txt bitdata_ramt.txt
endif
ifneq ($(RAM_SUFFIX),_8k)
	cp cached_ramb_8k.txt bitdata_ramb_8k.txt
	cp cached_ramt_8k.txt bitdata_ramt_8k.txt
endif
ifneq ($(RAM_SUFFIX),_5k)
	cp cached_dsp0_5k.txt bitdata_dsp0_5k.txt
	cp cached_dsp1_5k.txt bitdata_dsp1_5k.txt
	cp cached_dsp2_5k.txt bitdata_dsp2_5k.txt
	cp cached_dsp3_5k.txt bitdata_dsp3_5k.txt
	cp cached_ipcon_5k.txt bitdata_ipcon_5k.txt
endif
	ICEDEVICE=$(DEVICECLASS) $(PYTHON3) database.py
	$(PYTHON3) export.py
	diff -U0 cached_io.txt bitdata_io.txt || cp -v bitdata_io.txt cached_io.txt
	diff -U0 cached_logic.txt bitdata_logic.txt || cp -v bitdata_logic.txt cached_logic.txt
	diff -U0 cached_ramb$(RAM_SUFFIX).txt bitdata_ramb$(RAM_SUFFIX).txt || cp -v bitdata_ramb$(RAM_SUFFIX).txt cached_ramb$(RAM_SUFFIX).txt
	diff -U0 cached_ramt$(RAM_SUFFIX).txt bitdata_ramt$(RAM_SUFFIX).txt || cp -v bitdata_ramt$(RAM_SUFFIX).txt cached_ramt$(RAM_SUFFIX).txt
	diff -U0 cached_dsp0_5k.txt bitdata_dsp0_5k.txt || cp -v bitdata_dsp0_5k.txt cached_dsp0_5k.txt
	diff -U0 cached_dsp1_5k.txt bitdata_dsp1_5k.txt || cp -v bitdata_dsp1_5k.txt cached_dsp1_5k.txt
	diff -U0 cached_dsp2_5k.txt bitdata_dsp2_5k.txt || cp -v bitdata_dsp2_5k.txt cached_dsp2_5k.txt
	diff -U0 cached_dsp3_5k.txt bitdata_dsp3_5k.txt || cp -v bitdata_dsp3_5k.txt cached_dsp3_5k.txt
	diff -U0 cached_ipcon_5k.txt bitdata_ipcon_5k.txt || cp -v bitdata_ipcon_5k.txt cached_ipcon_5k.txt

timings:
ifeq ($(DEVICECLASS),5k)
	cp tmedges.txt tmedges.tmp
	set -e; for f in work_$(DEVICECLASS)_*/*.vsb; do echo $$f; sed '/defparam/d' < $$f > $$f.fixed;  yosys -q -f verilog -s tmedges.ys $$f.fixed; $(PYTHON3) rename_dsps.py $$f; done
	sort -u tmedges.tmp > tmedges.txt && rm -f tmedges.tmp
	$(PYTHON3) timings.py -t timings_up5k.txt work_*/*.sdf > timings_up5k.new
	mv timings_up5k.new timings_up5k.txt
else
ifeq ($(DEVICECLASS),u4k)
	cp tmedges.txt tmedges.tmp
	set -e; for f in work_$(DEVICECLASS)_*/*.vsb; do echo $$f; sed '/defparam/d' < $$f > $$f.fixed;  yosys -q -f verilog -s tmedges.ys $$f.fixed; $(PYTHON3) rename_dsps.py $$f; done
	sort -u tmedges.tmp > tmedges.txt && rm -f tmedges.tmp
	$(PYTHON3) timings.py -t timings_u4k.txt work_*/*.sdf > timings_u4k.new
	mv timings_u4k.new timings_u4k.txt
else
ifeq ($(DEVICECLASS),8k)
	cp tmedges.txt tmedges.tmp
	set -e; for f in work_$(DEVICECLASS)_*/*.vsb; do echo $$f; yosys -q -f verilog -s tmedges.ys $$f; done
	sort -u tmedges.tmp > tmedges.txt && rm -f tmedges.tmp
	$(PYTHON3) timings.py -t timings_hx8k.txt work_*/*.sdf > timings_hx8k.new
	mv timings_hx8k.new timings_hx8k.txt
	$(PYTHON3) timings.py -t timings_lp8k.txt work_*/*.slp > timings_lp8k.new
	mv timings_lp8k.new timings_lp8k.txt
else
 ifeq ($(DEVICECLASS),384)
	cp tmedges.txt tmedges.tmp
	set -e; for f in work_$(DEVICECLASS)_*/*.vsb; do echo $$f; yosys -q -f verilog -s tmedges.ys $$f; done
	sort -u tmedges.tmp > tmedges.txt && rm -f tmedges.tmp
	$(PYTHON3) timings.py -t timings_lp384.txt work_*/*.slp > timings_lp384.new
	mv timings_lp384.new timings_lp384.txt
 else
	cp tmedges.txt tmedges.tmp
	set -e; for f in work_$(DEVICECLASS)_*/*.vsb; do echo $$f; yosys -q -f verilog -s tmedges.ys $$f; done
	sort -u tmedges.tmp > tmedges.txt && rm -f tmedges.tmp
	$(PYTHON3) timings.py -t timings_hx1k.txt work_*/*.sdf > timings_hx1k.new
	mv timings_hx1k.new timings_hx1k.txt
	$(PYTHON3) timings.py -t timings_lp1k.txt work_*/*.slp > timings_lp1k.new
	mv timings_lp1k.new timings_lp1k.txt
 endif
endif
endif
endif
timings_html:
	$(PYTHON3) timings.py -h tmedges.txt -t timings_hx1k.txt -l "HX1K with default temp/volt settings" > timings_hx1k.html
	$(PYTHON3) timings.py -h tmedges.txt -t timings_hx8k.txt -l "HX8K with default temp/volt settings" > timings_hx8k.html
	$(PYTHON3) timings.py -h tmedges.txt -t timings_lp1k.txt -l "LP1K with default temp/volt settings" > timings_lp1k.html
	$(PYTHON3) timings.py -h tmedges.txt -t timings_lp8k.txt -l "LP8K with default temp/volt settings" > timings_lp8k.html
	$(PYTHON3) timings.py -h tmedges.txt -t timings_lp384.txt -l "LP384 with default temp/volt settings" > timings_lp384.html
	$(PYTHON3) timings.py -h tmedges.txt -t timings_up5k.txt -l "UP5K with default temp/volt settings" > timings_up5k.html
	$(PYTHON3) timings.py -h tmedges.txt -t timings_u4k.txt -l "U4K with default temp/volt settings" > timings_u4k.html
data_cached.txt: cached_io.txt cached_logic.txt cached_ramb$(RAM_SUFFIX).txt cached_ramt$(RAM_SUFFIX).txt cached_dsp0_5k.txt cached_dsp1_5k.txt cached_dsp2_5k.txt cached_dsp3_5k.txt cached_ipcon_5k.txt
	gawk '{ print "io", $$0; }' cached_io.txt > data_cached.new
	gawk '{ print "logic", $$0; }' cached_logic.txt >> data_cached.new
	gawk '{ print "ramb$(RAM_SUFFIX)", $$0; }' cached_ramb$(RAM_SUFFIX).txt >> data_cached.new
	gawk '{ print "ramt$(RAM_SUFFIX)", $$0; }' cached_ramt$(RAM_SUFFIX).txt >> data_cached.new

	gawk '{ print "dsp0_5k", $$0; }' cached_dsp0_5k.txt >> data_cached.new
	gawk '{ print "dsp1_5k", $$0; }' cached_dsp1_5k.txt >> data_cached.new
	gawk '{ print "dsp2_5k", $$0; }' cached_dsp2_5k.txt >> data_cached.new
	gawk '{ print "dsp3_5k", $$0; }' cached_dsp3_5k.txt >> data_cached.new
	gawk '{ print "ipcon_5k", $$0; }' cached_ipcon_5k.txt >> data_cached.new

	mv data_cached.new data_cached.txt

bitdata_io.txt: data_cached.txt $(addprefix data_$(DEVICECLASS)_,$(addsuffix .txt,$(TESTS)))
	grep ^io $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

bitdata_logic.txt: data_cached.txt $(addprefix data_$(DEVICECLASS)_,$(addsuffix .txt,$(TESTS)))
	grep ^logic $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

bitdata_ramb$(RAM_SUFFIX).txt: data_cached.txt $(addprefix data_$(DEVICECLASS)_,$(addsuffix .txt,$(TESTS)))
	grep ^ramb$(RAM_SUFFIX) $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

bitdata_ramt$(RAM_SUFFIX).txt: data_cached.txt $(addprefix data_$(DEVICECLASS)_,$(addsuffix .txt,$(TESTS)))
	grep ^ramt$(RAM_SUFFIX) $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

bitdata_dsp0_5k.txt: data_cached.txt $(addprefix data_$(DEVICECLASS)_,$(addsuffix .txt,$(TESTS)))
	grep ^dsp0_5k $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@	

bitdata_dsp1_5k.txt: data_cached.txt $(addprefix data_$(DEVICECLASS)_,$(addsuffix .txt,$(TESTS)))
	grep ^dsp1_5k $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@	
		
bitdata_dsp2_5k.txt: data_cached.txt $(addprefix data_$(DEVICECLASS)_,$(addsuffix .txt,$(TESTS)))
	grep ^dsp2_5k $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@	
			
bitdata_dsp3_5k.txt: data_cached.txt $(addprefix data_$(DEVICECLASS)_,$(addsuffix .txt,$(TESTS)))
	grep ^dsp3_5k $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@	

bitdata_ipcon_5k.txt: data_cached.txt $(addprefix data_$(DEVICECLASS)_,$(addsuffix .txt,$(TESTS)))
	grep ^ipcon_5k $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@	

datafiles: $(addprefix data_,$(addsuffix .txt,$(TESTS)))

../icepack/icepack:
	$(MAKE) -C ../icepack

define data_template
data_$(DEVICECLASS)_$(1).txt: make_$(1).py ../icepack/icepack
	ICEDEVICE=$(DEVICECLASS) $(PYTHON3) make_$(1).py
	+ICEDEV=$(DEVICE) $(MAKE) -C work_$(DEVICECLASS)_$(1)
	ICEDEVICE=$(DEVICECLASS) $(PYTHON3) extract.py work_$(DEVICECLASS)_$(1)/*.glb > $$@
endef

$(foreach test,$(TESTS),$(eval $(call data_template,$(test))))

%.ok: %.bin
	bash check.sh $<

check: $(addsuffix .ok,$(basename $(wildcard work_$(DEVICECLASS)_binop/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_$(DEVICECLASS)_pin2pin/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_$(DEVICECLASS)_mesh/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_$(DEVICECLASS)_fanout/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_$(DEVICECLASS)_logic/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_$(DEVICECLASS)_cluster/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_$(DEVICECLASS)_iopack/*.bin)))
check: $(addsuffix .ok,$(basename $(wildcard work_$(DEVICECLASS)_pll/*.bin)))

clean:
	rm -rf work_$(DEVICECLASS)_*
	rm -rf data_*.txt
	rm -rf bitdata_*.txt
	rm -rf database_*.txt
	rm -rf timings_*.html

.PHONY: database datafiles check clean
