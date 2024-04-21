PROJ = blinky

PIN_DEF = blinky.pcf
DEVICE = hx1k
PACKAGE = tq144
icebox_vlog_test_params := s l p c sl sp sc lp lc cp slp slc scp lcp slcp

all: test

test: icebox_vlog_test

# Create test target list for icebox_vlog with different parameter options
# composed of the case with no options, all of the options specified in
# $(icebox_vlog_test_params), and all of the same cases with -C (Verilog-1995)
# compatibilty.
icebox_vlog_output := $(PROJ)_syn.v $(PROJ)-C_syn.v \
	$(foreach case,$(icebox_vlog_test_params),$(PROJ)-$(case)_syn.v) \
	$(foreach case,$(icebox_vlog_test_params),$(PROJ)-C$(case)_syn.v)
icebox_vlog_iverilog_testlist := $(PROJ)_syntb $(PROJ)-C_syntb \
	$(foreach case,$(icebox_vlog_test_params),$(PROJ)-$(case)_syntb) \
	$(foreach case,$(icebox_vlog_test_params),$(PROJ)-C$(case)_syntb)
icebox_vlog_yosys_testlist := $(PROJ)_syn.json $(PROJ)-C_syn.json \
	$(foreach case,$(icebox_vlog_test_params),$(PROJ)-$(case)_syn.json) \
	$(foreach case,$(icebox_vlog_test_params),$(PROJ)-C$(case)_syn.json)
icebox_vlog_test: $(icebox_vlog_output) $(icebox_vlog_iverilog_testlist) $(icebox_vlog_yosys_testlist)

%.json: %.v
	yosys -p 'synth_ice40 -top $(PROJ) -json $@' $<

%.asc: $(PIN_DEF) %.json
	nextpnr-ice40 --$(DEVICE) --package $(PACKAGE) --asc $@ --pcf $< --json $*.json

%.bin: %.asc
	icepack $< $@

%.rpt: %.asc
	icetime -d $(DEVICE) -mtr $@ $<

%_tb: %_tb.v %.v
	iverilog -o $@ $^

%_tb.vcd: %_tb
	vvp -N $< +vcd=$@

get_test_params = $(subst p,p $(PIN_DEF),\
	$(filter-out $(1),\
	$(1:$(PROJ)-%_syn.v=-%)))
%_syn.v: $(PROJ).asc
	../icebox_vlog.py -n blinky $(call get_test_params,$@) $^ > $@

%_syntb: %_stb.v %_syn.v
	iverilog -o $@ $^

%_syntb.vcd: %_syntb
	vvp -N $< +vcd=$@

sim: $(PROJ)_tb.vcd

postsim: $(PROJ)_syntb.vcd

prog: $(PROJ).bin
	iceprog $<

sudo-prog: $(PROJ).bin
	@echo 'Executing prog as root!!!'
	sudo iceprog $<

clean:
	rm -f *.json $(PROJ).asc $(PROJ).rpt $(PROJ).bin \
		*.vcd *_tb *_syntb *_syn.v

.SECONDARY:
.PHONY: all prog clean test icebox_vlog_test
