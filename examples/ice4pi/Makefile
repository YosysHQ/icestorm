example.bin: example.v ice4pi.pcf
	yosys example.ys
	arachne-pnr -p ice4pi.pcf example.blif -o example.txt
	icebox_explain example.txt > example.ex
	icepack example.txt example.bin

load: example.bin
	./ice4pi_prog example.bin

clean:
	rm -f example.blif example.txt example.ex example.bin
