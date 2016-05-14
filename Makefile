include config.mk

all:
	$(MAKE) -C icebox
	$(MAKE) -C icepack
	$(MAKE) -C iceprog
	$(MAKE) -C icemulti
	$(MAKE) -C icepll
	$(MAKE) -C icetime
	$(MAKE) -C icebram

clean:
	$(MAKE) -C icebox clean
	$(MAKE) -C icepack clean
	$(MAKE) -C iceprog clean
	$(MAKE) -C icemulti clean
	$(MAKE) -C icepll clean
	$(MAKE) -C icetime clean
	$(MAKE) -C icebram clean

install:
	$(MAKE) -C icebox install
	$(MAKE) -C icepack install
	$(MAKE) -C iceprog install
	$(MAKE) -C icemulti install
	$(MAKE) -C icepll install
	$(MAKE) -C icetime install
	$(MAKE) -C icebram install

uninstall:
	$(MAKE) -C icebox uninstall
	$(MAKE) -C icepack uninstall
	$(MAKE) -C iceprog uninstall
	$(MAKE) -C icemulti uninstall
	$(MAKE) -C icepll uninstall
	$(MAKE) -C icetime uninstall
	$(MAKE) -C icebram uninstall

mxebin: clean
	$(MAKE) MXE=1
	rm -rf icestorm-win32 && mkdir icestorm-win32
	cp icebox/chipdb-*.txt icepack/*.exe iceprog/*.exe icestorm-win32/
	cp icemulti/*.exe icepll/*.exe icetime/*.exe icestorm-win32/
	zip -r icestorm-win32.zip icestorm-win32/

.PHONY: all clean install uninstall

