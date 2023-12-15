all: config.bin

prog: config.bin
	sudo iceprog config.bin

sudo-prog: config.bin
	@echo 'Executing prog as root!!!'
	sudo iceprog config.bin

config.bin: app0.bin app1.bin app2.bin app3.bin
	icemulti -v -A16 -p0 -o config.bin app0.bin app1.bin app2.bin app3.bin

app%.bin: app%.v icestick.pcf
	yosys -p "synth_ice40 -top top -json $(basename $<).json" $<
	nextpnr-ice40 --hx1k --package tq144 --asc $(basename $<).asc --pcf icestick.pcf --json $(basename $<).json
	icetime -d hx1k -c 25 $(basename $<).asc
	icepack $(basename $<).asc $(basename $<).bin

clean:
	rm -f app?.asc app?.bin app?.json config.bin

.PHONY: prog sudo-prog clean
