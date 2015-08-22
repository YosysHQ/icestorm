CXX ?= clang

all:
	$(MAKE) -C icebox
	$(MAKE) -C icepack
	$(MAKE) -C iceprog
	$(MAKE) -C icemulti

clean:
	$(MAKE) -C icebox clean
	$(MAKE) -C icepack clean
	$(MAKE) -C iceprog clean
	$(MAKE) -C icemulti clean

install:
	$(MAKE) -C icebox install
	$(MAKE) -C icepack install
	$(MAKE) -C iceprog install
	$(MAKE) -C icemulti install

uninstall:
	$(MAKE) -C icebox uninstall
	$(MAKE) -C icepack uninstall
	$(MAKE) -C iceprog uninstall
	$(MAKE) -C icemulti uninstall

.PHONY: all clean install uninstall

