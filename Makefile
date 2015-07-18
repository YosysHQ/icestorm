
all:
	$(MAKE) -C icebox
	$(MAKE) -C icepack
	$(MAKE) -C iceprog

install:
	$(MAKE) -C icebox install
	$(MAKE) -C icepack install
	$(MAKE) -C iceprog install

uninstall:
	$(MAKE) -C icebox uninstall
	$(MAKE) -C icepack uninstall
	$(MAKE) -C iceprog uninstall

.PHONY: all install uninstall

