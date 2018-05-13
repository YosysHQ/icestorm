include ../config.mk

all: chipdb-384.txt chipdb-1k.txt chipdb-8k.txt chipdb-5k.txt chipdb-lm4k.txt

chipdb-384.txt: icebox.py iceboxdb.py icebox_chipdb.py
	python3 icebox_chipdb.py -3 > chipdb-384.new
	mv chipdb-384.new chipdb-384.txt

chipdb-1k.txt: icebox.py iceboxdb.py icebox_chipdb.py
	python3 icebox_chipdb.py > chipdb-1k.new
	mv chipdb-1k.new chipdb-1k.txt

chipdb-5k.txt: icebox.py iceboxdb.py icebox_chipdb.py
	python3 icebox_chipdb.py -5 > chipdb-5k.new
	mv chipdb-5k.new chipdb-5k.txt

chipdb-lm4k.txt: icebox.py iceboxdb.py icebox_chipdb.py
	python3 icebox_chipdb.py -4 > chipdb-lm4k.new
	mv chipdb-lm4k.new chipdb-lm4k.txt

chipdb-8k.txt: icebox.py iceboxdb.py icebox_chipdb.py
	python3 icebox_chipdb.py -8 > chipdb-8k.new
	mv chipdb-8k.new chipdb-8k.txt

check: all
	python3 tc_xlat_netnames.py
	python3 tc_rxlat_netnames.py
	python3 tc_logic_xpr.py

clean:
	rm -f chipdb-1k.txt chipdb-8k.txt chipdb-384.txt chipdb-5k.txt chipdb-lm4k.txt
	rm -f icebox.pyc iceboxdb.pyc

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/share/icebox
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp chipdb-384.txt    $(DESTDIR)$(PREFIX)/share/icebox/
	cp chipdb-1k.txt     $(DESTDIR)$(PREFIX)/share/icebox/
	cp chipdb-8k.txt     $(DESTDIR)$(PREFIX)/share/icebox/
	cp chipdb-5k.txt     $(DESTDIR)$(PREFIX)/share/icebox/
	cp chipdb-lm4k.txt   $(DESTDIR)$(PREFIX)/share/icebox/
	cp icebox.py         $(DESTDIR)$(PREFIX)/bin/icebox.py
	cp iceboxdb.py       $(DESTDIR)$(PREFIX)/bin/iceboxdb.py
	cp icebox_chipdb.py  $(DESTDIR)$(PREFIX)/bin/icebox_chipdb$(PY_EXE)
	cp icebox_diff.py    $(DESTDIR)$(PREFIX)/bin/icebox_diff$(PY_EXE)
	cp icebox_explain.py $(DESTDIR)$(PREFIX)/bin/icebox_explain$(PY_EXE)
	cp icebox_asc2hlc.py $(DESTDIR)$(PREFIX)/bin/icebox_asc2hlc$(PY_EXE)
	cp icebox_hlc2asc.py $(DESTDIR)$(PREFIX)/bin/icebox_hlc2asc$(PY_EXE)
	cp icebox_colbuf.py  $(DESTDIR)$(PREFIX)/bin/icebox_colbuf$(PY_EXE)
	cp icebox_html.py    $(DESTDIR)$(PREFIX)/bin/icebox_html$(PY_EXE)
	cp icebox_maps.py    $(DESTDIR)$(PREFIX)/bin/icebox_maps$(PY_EXE)
	cp icebox_vlog.py    $(DESTDIR)$(PREFIX)/bin/icebox_vlog$(PY_EXE)
	cp icebox_stat.py    $(DESTDIR)$(PREFIX)/bin/icebox_stat$(PY_EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox.py
	rm -f $(DESTDIR)$(PREFIX)/bin/iceboxdb.py
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox_chipdb$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox_diff$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox_explain$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox_asc2hlc$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox_hlc2asc$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox_colbuf$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox_html$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox_maps$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox_vlog$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/icebox_stat$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/share/icebox/chipdb-384.txt
	rm -f $(DESTDIR)$(PREFIX)/share/icebox/chipdb-1k.txt
	rm -f $(DESTDIR)$(PREFIX)/share/icebox/chipdb-8k.txt
	rm -f $(DESTDIR)$(PREFIX)/share/icebox/chipdb-lm4k.txt
	-rmdir $(DESTDIR)$(PREFIX)/share/icebox

.PHONY: all check clean install uninstall
