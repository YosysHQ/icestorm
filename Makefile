include config.mk

SUBDIRS := icebox icepack icemulti icepll icebram icetime
ifeq ($(ICEPROG),1)
SUBDIRS += iceprog
endif

all: $(addsuffix .all,$(SUBDIRS))
$(addsuffix .all,$(SUBDIRS)):
	$(MAKE) -C $(basename $@) all

clean install uninstall:
	for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir $@ || exit; \
	done

mxebin: clean
	$(MAKE) MXE=1
	rm -rf icestorm-win32 && mkdir icestorm-win32
	cp icebox/chipdb-*.txt icepack/*.exe iceprog/*.exe icestorm-win32/
	cp icemulti/*.exe icepll/*.exe icetime/*.exe icestorm-win32/
	zip -r icestorm-win32.zip icestorm-win32/

.PHONY: all clean install uninstall

