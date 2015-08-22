
export LC_ALL=C

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
TESTS += ram40
TESTS += pll

EIGTHK = _8k

database: bitdata_io.txt bitdata_logic.txt bitdata_ramb$(EIGTHK).txt bitdata_ramt$(EIGTHK).txt
ifeq ($(EIGTHK),_8k)
	cp cached_ramb.txt bitdata_ramb.txt
	cp cached_ramt.txt bitdata_ramt.txt
else
	cp cached_ramb_8k.txt bitdata_ramb_8k.txt
	cp cached_ramt_8k.txt bitdata_ramt_8k.txt
endif
	python3 database.py
	python3 export.py
	diff -U0 cached_io.txt bitdata_io.txt || cp -v bitdata_io.txt cached_io.txt
	diff -U0 cached_logic.txt bitdata_logic.txt || cp -v bitdata_logic.txt cached_logic.txt
	diff -U0 cached_ramb.txt bitdata_ramb.txt || cp -v bitdata_ramb.txt cached_ramb.txt
	diff -U0 cached_ramt.txt bitdata_ramt.txt || cp -v bitdata_ramt.txt cached_ramt.txt
	diff -U0 cached_ramb_8k.txt bitdata_ramb_8k.txt || cp -v bitdata_ramb_8k.txt cached_ramb_8k.txt
	diff -U0 cached_ramt_8k.txt bitdata_ramt_8k.txt || cp -v bitdata_ramt_8k.txt cached_ramt_8k.txt

data_cached.txt: cached_io.txt cached_logic.txt cached_ramb$(EIGTHK).txt cached_ramt$(EIGTHK).txt
	gawk '{ print "io", $$0; }' cached_io.txt > data_cached.new
	gawk '{ print "logic", $$0; }' cached_logic.txt >> data_cached.new
	gawk '{ print "ramb$(EIGTHK)", $$0; }' cached_ramb$(EIGTHK).txt >> data_cached.new
	gawk '{ print "ramt$(EIGTHK)", $$0; }' cached_ramt$(EIGTHK).txt >> data_cached.new
	mv data_cached.new data_cached.txt

bitdata_io.txt: data_cached.txt $(addprefix data_,$(addsuffix .txt,$(TESTS)))
	grep ^io $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

bitdata_logic.txt: data_cached.txt $(addprefix data_,$(addsuffix .txt,$(TESTS)))
	grep ^logic $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

bitdata_ramb$(EIGTHK).txt: data_cached.txt $(addprefix data_,$(addsuffix .txt,$(TESTS)))
	grep ^ramb$(EIGTHK) $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

bitdata_ramt$(EIGTHK).txt: data_cached.txt $(addprefix data_,$(addsuffix .txt,$(TESTS)))
	grep ^ramt$(EIGTHK) $^ | tr -s ' ' | tr -d '\r' | cut -f2- -d' ' | sort -u > $@

datafiles: $(addprefix data_,$(addsuffix .txt,$(TESTS)))

../icepack/icepack:
	$(MAKE) -C ../icepack

define data_template
data_$(1).txt: make_$(1).py ../icepack/icepack
ifeq ($(EIGTHK),_8k)
	ICE8KPINS=1 python3 make_$(1).py
	ICEDEV=hx8k-ct256 $(MAKE) -C work_$(1)
	python3 extract.py -8 work_$(1)/*.glb > $$@
else
	python3 make_$(1).py
	$(MAKE) -C work_$(1)
	python3 extract.py work_$(1)/*.glb > $$@
endif
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

.PHONY: database datafiles check clean

