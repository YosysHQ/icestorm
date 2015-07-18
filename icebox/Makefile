
chipdb: chipdb-1k.txt

chipdb-1k.txt: icebox.py iceboxdb.py icebox_chipdb.py
	python icebox_chipdb.py > chipdb-1k.new
	mv chipdb-1k.new chipdb-1k.txt

install: chipdb
	mkdir -p /usr/local/share/icebox
	cp chipdb-1k.txt     /usr/local/share/icebox/
	cp icebox.py         /usr/local/bin/icebox.py
	cp iceboxdb.py       /usr/local/bin/iceboxdb.py
	cp icebox_chipdb.py  /usr/local/bin/icebox_chipdb
	cp icebox_diff.py    /usr/local/bin/icebox_diff
	cp icebox_explain.py /usr/local/bin/icebox_explain
	cp icebox_html.py    /usr/local/bin/icebox_html
	cp icebox_maps.py    /usr/local/bin/icebox_maps
	cp icebox_vlog.py    /usr/local/bin/icebox_vlog

uninstall:
	rm -f /usr/local/bin/icebox.py
	rm -f /usr/local/bin/iceboxdb.py
	rm -f /usr/local/bin/icebox_chipdb
	rm -f /usr/local/bin/icebox_diff
	rm -f /usr/local/bin/icebox_explain
	rm -f /usr/local/bin/icebox_html
	rm -f /usr/local/bin/icebox_maps
	rm -f /usr/local/bin/icebox_vlog
	rm -f /usr/local/share/icebox/chipdb-1k.txt
	-rmdir /usr/local/share/icebox

.PHONY: install uninstall

