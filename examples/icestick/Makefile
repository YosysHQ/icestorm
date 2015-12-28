PROJ = example
PIN_DEF = icestick.pcf
DEVICE = 1k

all: $(PROJ).bin

%.blif: %.v
	yosys -p 'synth_ice40 -top top -blif $@' $<

%.txt: $(PIN_DEF) %.blif
	arachne-pnr -d $(DEVICE) -o $@ -p $^

%.bin: %.txt
	icepack $< $@

prog:
	iceprog $(PROJ).bin

clean:
	rm -f *.blif *.txt *.bin

.PHONY: all prog clean
