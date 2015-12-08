all: example.bin

example.blif: example.v
	yosys -p 'synth_ice40 -top top -blif example.blif' example.v

example.txt: example.blif icestick.pcf
	arachne-pnr -d 1k -o example.txt -p icestick.pcf example.blif

example.bin: example.txt
	icepack example.txt example.bin

prog:
	iceprog example.bin

clean:
	rm -f example.blif example.txt example.bin

.PHONY: all prog clean
