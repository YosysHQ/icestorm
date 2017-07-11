include config.mk

SUBDIRS = icebox icepack iceprog icemulti icepll icetime icebram

all check clean install uninstall:
	for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir $@ || exit; \
	done

mxebin: clean
	$(MAKE) MXE=1
	rm -rf icestorm-win32 && mkdir icestorm-win32
	cp icebox/chipdb-*.txt icepack/*.exe iceprog/*.exe icestorm-win32/
	cp icemulti/*.exe icepll/*.exe icetime/*.exe icestorm-win32/
	zip -r icestorm-win32.zip icestorm-win32/

.PHONY: all check clean install uninstall

