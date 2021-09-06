include ../config.mk

ifneq ($(shell uname -s),Darwin)
  SED_I = sed -i
else
  SED_I = sed -i ''
endif

all: chipdb-384.txt chipdb-1k.txt chipdb-8k.txt chipdb-5k.txt chipdb-lm4k.txt chipdb-u4k.txt

chipdb-384.txt: icebox.py iceboxdb.py icebox_chipdb.py
	$(PYTHON3) icebox_chipdb.py -3 > chipdb-384.new
	mv chipdb-384.new chipdb-384.txt

chipdb-1k.txt: icebox.py iceboxdb.py icebox_chipdb.py
	$(PYTHON3) icebox_chipdb.py > chipdb-1k.new
	mv chipdb-1k.new chipdb-1k.txt

chipdb-5k.txt: icebox.py iceboxdb.py icebox_chipdb.py
	$(PYTHON3) icebox_chipdb.py -5 > chipdb-5k.new
	mv chipdb-5k.new chipdb-5k.txt

chipdb-u4k.txt: icebox.py iceboxdb.py icebox_chipdb.py
	$(PYTHON3) icebox_chipdb.py -u > chipdb-u4k.new
	mv chipdb-u4k.new chipdb-u4k.txt

chipdb-lm4k.txt: icebox.py iceboxdb.py icebox_chipdb.py
	$(PYTHON3) icebox_chipdb.py -4 > chipdb-lm4k.new
	mv chipdb-lm4k.new chipdb-lm4k.txt

chipdb-8k.txt: icebox.py iceboxdb.py icebox_chipdb.py
	$(PYTHON3) icebox_chipdb.py -8 > chipdb-8k.new
	mv chipdb-8k.new chipdb-8k.txt

check: all
	$(PYTHON3) tc_xlat_netnames.py
	$(PYTHON3) tc_rxlat_netnames.py
	$(PYTHON3) tc_logic_xpr.py

clean:
	rm -f chipdb-1k.txt chipdb-8k.txt chipdb-384.txt chipdb-5k.txt chipdb-lm4k.txt chipdb-u4k.txt
	rm -f icebox.pyc iceboxdb.pyc

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp chipdb-384.txt    $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/
	cp chipdb-1k.txt     $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/
	cp chipdb-8k.txt     $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/
	cp chipdb-5k.txt     $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/
	cp chipdb-u4k.txt    $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/
	cp chipdb-lm4k.txt   $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/
	cp icebox.py         $(DESTDIR)$(PREFIX)/bin/$(subst -,_,$(PROGRAM_PREFIX))icebox.py
	cp iceboxdb.py       $(DESTDIR)$(PREFIX)/bin/$(subst -,_,$(PROGRAM_PREFIX))iceboxdb.py
	cp icebox_chipdb.py  $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_chipdb$(PY_EXE)
	cp icebox_diff.py    $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_diff$(PY_EXE)
	cp icebox_explain.py $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_explain$(PY_EXE)
	cp icebox_asc2hlc.py $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_asc2hlc$(PY_EXE)
	cp icebox_hlc2asc.py $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_hlc2asc$(PY_EXE)
	cp icebox_colbuf.py  $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_colbuf$(PY_EXE)
	cp icebox_html.py    $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_html$(PY_EXE)
	cp icebox_maps.py    $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_maps$(PY_EXE)
	cp icebox_vlog.py    $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_vlog$(PY_EXE)
	cp icebox_stat.py    $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_stat$(PY_EXE)
	$(SED_I) 's+import iceboxdb+import $(subst -,_,$(PROGRAM_PREFIX))iceboxdb as iceboxdb+g' $(DESTDIR)$(PREFIX)/bin/$(subst -,_,$(PROGRAM_PREFIX))icebox.py
	$(SED_I) 's+import icebox+import $(subst -,_,$(PROGRAM_PREFIX))icebox as icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_chipdb$(PY_EXE)
	$(SED_I) 's+import icebox+import $(subst -,_,$(PROGRAM_PREFIX))icebox as icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_diff$(PY_EXE)
	$(SED_I) 's+from icebox+from $(subst -,_,$(PROGRAM_PREFIX))icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_diff$(PY_EXE)
	$(SED_I) 's+import icebox+import $(subst -,_,$(PROGRAM_PREFIX))icebox as icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_explain$(PY_EXE)
	$(SED_I) 's+from icebox+from $(subst -,_,$(PROGRAM_PREFIX))icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_explain$(PY_EXE)
	$(SED_I) 's+import icebox+import $(subst -,_,$(PROGRAM_PREFIX))icebox as icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_asc2hlc$(PY_EXE)
	$(SED_I) 's+from icebox+from $(subst -,_,$(PROGRAM_PREFIX))icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_asc2hlc$(PY_EXE)
	$(SED_I) 's+import icebox+import $(subst -,_,$(PROGRAM_PREFIX))icebox as icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_hlc2asc$(PY_EXE)
	$(SED_I) 's+from icebox+from $(subst -,_,$(PROGRAM_PREFIX))icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_hlc2asc$(PY_EXE)
	$(SED_I) 's+import icebox+import $(subst -,_,$(PROGRAM_PREFIX))icebox as icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_colbuf$(PY_EXE)
	$(SED_I) 's+from icebox+from $(subst -,_,$(PROGRAM_PREFIX))icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_colbuf$(PY_EXE)
	$(SED_I) 's+import icebox+import $(subst -,_,$(PROGRAM_PREFIX))icebox as icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_html$(PY_EXE)
	$(SED_I) 's+from icebox+from $(subst -,_,$(PROGRAM_PREFIX))icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_html$(PY_EXE)
	$(SED_I) 's+import icebox+import $(subst -,_,$(PROGRAM_PREFIX))icebox as icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_maps$(PY_EXE)
	$(SED_I) 's+from icebox+from $(subst -,_,$(PROGRAM_PREFIX))icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_maps$(PY_EXE)
	$(SED_I) 's+import icebox+import $(subst -,_,$(PROGRAM_PREFIX))icebox as icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_vlog$(PY_EXE)
	$(SED_I) 's+from icebox+from $(subst -,_,$(PROGRAM_PREFIX))icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_vlog$(PY_EXE)
	$(SED_I) 's+/usr/local/share/icebox+$(PREFIX)/share/$(PROGRAM_PREFIX)icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_vlog$(PY_EXE)
	$(SED_I) 's+import icebox+import $(subst -,_,$(PROGRAM_PREFIX))icebox as icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_stat$(PY_EXE)
	$(SED_I) 's+from icebox+from $(subst -,_,$(PROGRAM_PREFIX))icebox+g' $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_stat$(PY_EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(subst -,_,$(PROGRAM_PREFIX))cebox.py
	rm -f $(DESTDIR)$(PREFIX)/bin/$(subst -,_,$(PROGRAM_PREFIX))iceboxdb.py
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_chipdb$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_diff$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_explain$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_asc2hlc$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_hlc2asc$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_colbuf$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_html$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_maps$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_vlog$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PROGRAM_PREFIX)icebox_stat$(PY_EXE)
	rm -f $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/chipdb-384.txt
	rm -f $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/chipdb-1k.txt
	rm -f $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/chipdb-8k.txt
	rm -f $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/chipdb-lm4k.txt
	rm -f $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox/chipdb-u4k.txt
	-rmdir $(DESTDIR)$(PREFIX)/share/$(PROGRAM_PREFIX)icebox

.PHONY: all check clean install uninstall
