PROJ = example
PIN_DEF = iceblink.pcf
DEVICE = 1k

all: $(PROJ).bin

%.blif: %.v
	yosys -p 'synth_ice40 -top top -blif $@' $<

%.asc: $(PIN_DEF) %.blif
	arachne-pnr -d $(DEVICE) -o $@ -p $^ -P vq100

%.bin: %.asc
	icepack $< $@

prog: $(PROJ).bin
	iCEburn.py  -e -v -w  $<

sudo-prog: $(PROJ).bin
	@echo 'Executing prog as root!!!'
	iCEburn.py  -e -v -w  $<

clean:
	rm -f $(PROJ).blif $(PROJ).asc $(PROJ).bin

.PHONY: all prog clean
