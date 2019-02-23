#!/bin/bash
#
# Installing iCEcube2:
#  - Install iCEcube2.2015.08 in /opt/lscc/iCEcube2.2015.08
#  - Install License in /opt/lscc/iCEcube2.2015.08/license.dat
#
# Creating a project:
#  - <project_name>.v    ## HDL sources (use "top" as name for the top module)
#  - <project_name>.sdc  ## timing constraint file
#  - <project_name>.pcf  ## physical constraint file
#
# Running iCEcube2:
#  - bash icecube.sh [-1k|-8k|-384] <project_name>  ## creates <project_name>.bin
#
#
#
# Additional notes for installing iCEcube2 on 64 Bit Ubuntu:
#
# sudo apt-get install libc6-i386 zlib1g:i386 libxext6:i386 libpng12-0:i386 libsm6:i386
# sudo apt-get install libxi6:i386 libxrender1:i386 libxrandr2:i386 libxfixes3:i386
# sudo apt-get install libxcursor1:i386 libxinerama1:i386 libfreetype6:i386
# sudo apt-get install libfontconfig1:i386 libglib2.0-0:i386 libstdc++6:i386 libelf1:i386
#
# icecubedir="/opt/lscc/iCEcube2.2015.08"
# sudo sed -ri "1 s,/bin/sh,/bin/bash,;" $icecubedir/synpbase/bin/synplify_pro
# sudo sed -ri "1 s,/bin/sh,/bin/bash,;" $icecubedir/synpbase/bin/c_hdl
# sudo sed -ri "1 s,/bin/sh,/bin/bash,;" $icecubedir/synpbase/bin/syn_nfilter
# sudo sed -ri "1 s,/bin/sh,/bin/bash,;" $icecubedir/synpbase/bin/m_generic
#

scriptdir=${BASH_SOURCE%/*}
if [ -z "$scriptdir" ]; then scriptdir="."; fi

if [ "$1" == "-1k" ]; then
	ICEDEV=hx1k-tq144
	shift
fi

if [ "$1" == "-8k" ]; then
	ICEDEV=hx8k-ct256
	shift
fi

if [ "$1" == "-384" ]; then
	ICEDEV=lp384-cm49
	shift
fi

if [ "$1" == "-ul1k" ]; then
	ICEDEV=ul1k-cm36a
	shift
fi

if [ "$1" == "-up5k" ]; then
	ICEDEV=up5k-sg48
	shift
fi

if [ "$1" == "-lm4k" ]; then
	ICEDEV=lm4k-cm49
	shift
fi

if [ "$1" == "-u4k" ]; then
	ICEDEV=u4k-sg48
	shift
fi

set -ex
set -- ${1%.v}
icecubedir="${ICECUBEDIR:-/opt/lscc/iCEcube2.2015.08}"
if [ -d $icecubedir/LSE/bin/lin64 ]; then lin_lin64=lin64; else lin_lin64=lin; fi
export FOUNDRY="$icecubedir/LSE"
export SBT_DIR="$icecubedir/sbt_backend"
export SYNPLIFY_PATH="$icecubedir/synpbase"
export LM_LICENSE_FILE="$icecubedir/license.dat"
export TCL_LIBRARY="$icecubedir/sbt_backend/bin/linux/lib/tcl8.4"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH${LD_LIBRARY_PATH:+:}$icecubedir/sbt_backend/bin/linux/opt"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH${LD_LIBRARY_PATH:+:}$icecubedir/sbt_backend/bin/linux/opt/synpwrap"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH${LD_LIBRARY_PATH:+:}$icecubedir/sbt_backend/lib/linux/opt"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH${LD_LIBRARY_PATH:+:}$icecubedir/LSE/bin/${lin_lin64}"

case "${ICEDEV:-hx1k-tq144}" in
	hx1k-cb132)
		iCEPACKAGE="CB132"
		iCE40DEV="iCE40HX1K"
		;;
	hx1k-vq100)
		iCEPACKAGE="VQ100"
		iCE40DEV="iCE40HX1K"
		;;
	hx1k-tq144)
		iCEPACKAGE="TQ144"
		iCE40DEV="iCE40HX1K"
		;;
	hx4k-cb132)
		iCEPACKAGE="CB132"
		iCE40DEV="iCE40HX4K"
		;;
	hx4k-tq144)
		iCEPACKAGE="TQ144"
		iCE40DEV="iCE40HX4K"
		;;
	hx8k-cm225)
		iCEPACKAGE="CM225"
		iCE40DEV="iCE40HX8K"
		;;
	hx8k-ct256)
		iCEPACKAGE="CT256"
		iCE40DEV="iCE40HX8K"
		;;
	hx8k-cb132)
		iCEPACKAGE="CB132"
		iCE40DEV="iCE40HX8K"
		;;
	lp384-qn32)
		iCEPACKAGE="QN32"
		iCE40DEV="iCE40LP384"
		;;
	lp384-cm36)
		iCEPACKAGE="CM36"
		iCE40DEV="iCE40LP384"
		;;
	lp384-cm49)
		iCEPACKAGE="CM49"
		iCE40DEV="iCE40LP384"
		;;
        lp1k-swg16tr)
                iCEPACKAGE="SWG16TR"
                iCE40DEV="iCE40LP1K"
                ;;
        lp1k-cm36)
                iCEPACKAGE="CM36"
                iCE40DEV="iCE40LP1K"
                ;;
        lp1k-cm49)
                iCEPACKAGE="CM49"
                iCE40DEV="iCE40LP1K"
                ;;
        lp1k-cm81)
                iCEPACKAGE="CM81"
                iCE40DEV="iCE40LP1K"
                ;;
        lp1k-cm121)
                iCEPACKAGE="CM121"
                iCE40DEV="iCE40LP1K"
                ;;
        lp1k-qn84)
                iCEPACKAGE="QN84"
                iCE40DEV="iCE40LP1K"
                ;;
        lp1k-cb81)
                iCEPACKAGE="CB81"
                iCE40DEV="iCE40LP1K"
                ;;
        lp1k-cb121)
                iCEPACKAGE="CB121"
                iCE40DEV="iCE40LP1K"
                ;;
	lp4k-cm81)
		iCEPACKAGE="CM81"
		iCE40DEV="iCE40LP4K"
		;;
	lp4k-cm121)
		iCEPACKAGE="CM121"
		iCE40DEV="iCE40LP4K"
		;;
	lp4k-cm225)
		iCEPACKAGE="CM225"
		iCE40DEV="iCE40LP4K"
		;;
	lp8k-cm81)
		iCEPACKAGE="CM81"
		iCE40DEV="iCE40LP8K"
		;;
	lp8k-cm121)
		iCEPACKAGE="CM121"
		iCE40DEV="iCE40LP8K"
		;;
	lp8k-cm225)
		iCEPACKAGE="CM225"
		iCE40DEV="iCE40LP8K"
		;;
	ul1k-cm36a)
                iCEPACKAGE="CM36A"
                iCE40DEV="iCE40UL1K"
		;;
	ul1k-swg16)
                iCEPACKAGE="CM36A"
                iCE40DEV="iCE40UL1K"
		;;
	up5k-sg48)
		iCEPACKAGE="SG48"
		iCE40DEV="iCE40UP5K"
		;;
	up5k-uwg30)
		iCEPACKAGE="UWG30"
		iCE40DEV="iCE40UP5K"
		;;
	lm4k-cm49)
		iCEPACKAGE="CM49"
		iCE40DEV="iCE40LM4K"
		;;
	lm4k-cm36)
		iCEPACKAGE="CM36"
		iCE40DEV="iCE40LM4K"
		;;
	lm4k-swg25tr)
		iCEPACKAGE="SWG25TR"
		iCE40DEV="iCE40LM4K"
		;;
	lm2k-cm49)
		iCEPACKAGE="CM49"
		iCE40DEV="iCE40LM2K"
		;;
	lm2k-cm36)
		iCEPACKAGE="CM36"
		iCE40DEV="iCE40LM2K"
		;;
	lm2k-swg25tr)
		iCEPACKAGE="SWG25TR"
		iCE40DEV="iCE40LM2K"
		;;
	lm1k-cm49)
		iCEPACKAGE="CM49"
		iCE40DEV="iCE40LM1K"
		;;
	lm1k-cm36)
		iCEPACKAGE="CM36"
		iCE40DEV="iCE40LM1K"
		;;
	lm1k-swg25tr)
		iCEPACKAGE="SWG25TR"
		iCE40DEV="iCE40LM1K"
		;;
        u1k-sg48)
                iCEPACKAGE="SG48"
                iCE40DEV="iCE5LP1K"
                ;;
        u4k-sg48)
                iCEPACKAGE="SG48"
                iCE40DEV="iCE5LP4K"
                ;;
	*)
		echo "ERROR: Invalid \$ICEDEV device config '$ICEDEV'."
		exit 1
esac

case "$iCE40DEV" in
	iCE40HX1K)
		icetech="SBTiCE40"
		libfile="ice40HX1K.lib"
		devfile="ICE40P01.dev"
		;;
	iCE40HX4K)
		icetech="SBTiCE40"
		libfile="ice40HX8K.lib"
		devfile="ICE40P04.dev"
		;;
	iCE40HX8K)
		icetech="SBTiCE40"
		libfile="ice40HX8K.lib"
		devfile="ICE40P08.dev"
		;;
	iCE40LP384)
		icetech="SBTiCE40"
		libfile="ice40LP384.lib"
		devfile="ICE40P03.dev"
		;;
	iCE40LP1K)
		icetech="SBTiCE40"
		libfile="ice40LP1K.lib"
		devfile="ICE40P01.dev"
		;;
	iCE40LP4K)
		icetech="SBTiCE40"
		libfile="ice40LP8K.lib"
		devfile="ICE40P04.dev"
		;;
	iCE40LP8K)
		icetech="SBTiCE40"
		libfile="ice40LP8K.lib"
		devfile="ICE40P08.dev"
		;;
	iCE40UL1K)
		icetech="SBTiCE40UL"
		libfile="ice40BT1K.lib"
		devfile="ICE40T01.dev"
		;;
	iCE40UP5K)
		icetech="SBTiCE40UP"
		libfile="ice40UP5K.lib"
		devfile="ICE40T05.dev"
		;;
	iCE40LM1K)
		icetech="SBTiCE40LM"
		libfile="ice40LM4K.lib"
		devfile="ICE40R04.dev"
		;;
	iCE40LM2K)
		icetech="SBTiCE40LM"
		libfile="ice40LM4K.lib"
		devfile="ICE40R04.dev"
		;;
	iCE40LM4K)
		icetech="SBTiCE40LM"
		libfile="ice40LM4K.lib"
		devfile="ICE40R04.dev"
		;;
        iCE5LP1K)
                icetech="SBTiCE5LP"
                libfile="ice40TH4K.lib"
                devfile="ICE40T04.dev"
                ;;
        iCE5LP4K)
                icetech="SBTiCE5LP"
                libfile="ice40TH4K.lib"
                devfile="ICE40T04.dev"
                ;;
esac

(
rm -rf "$1.tmp"
mkdir -p "$1.tmp"
cp "$1.v" "$1.tmp/input.v"
if test -f "$1.sdc"; then cp "$1.sdc" "$1.tmp/input.sdc"; fi
if test -f "$1.pcf"; then cp "$1.pcf" "$1.tmp/input.pcf"; fi
cd "$1.tmp"

touch input.sdc
touch input.pcf

mkdir -p outputs/packer
mkdir -p outputs/placer
mkdir -p outputs/router
mkdir -p outputs/bitmap
mkdir -p outputs/netlist
mkdir -p netlist/Log/bitmap

cat > impl_syn.prj << EOT
add_file -verilog -lib work input.v
impl -add impl -type fpga

# implementation attributes
set_option -vlog_std v2001
set_option -project_relative_includes 1

# device options
set_option -technology $icetech
set_option -part $iCE40DEV
set_option -package $iCEPACKAGE
set_option -speed_grade
set_option -part_companion ""

# mapper_options
set_option -frequency auto
set_option -write_verilog 0
set_option -write_vhdl 0

# Silicon Blue iCE40
set_option -maxfan 10000
set_option -disable_io_insertion 0
set_option -pipe 1
set_option -retiming 0
set_option -update_models_cp 0
set_option -fixgatedclocks 2
set_option -fixgeneratedclocks 0

# NFilter
set_option -popfeed 0
set_option -constprop 0
set_option -createhierarchy 0

# sequential_optimization_options
set_option -symbolic_fsm_compiler 1

# Compiler Options
set_option -compiler_compatible 0
set_option -resource_sharing 1

# automatic place and route (vendor) options
set_option -write_apr_constraint 1

# set result format/file last
project -result_format edif
project -result_file impl.edf
impl -active impl
project -run synthesis -clean
EOT

cat > impl_lse.prj << EOT
#device
-a $icetech
-d $iCE40DEV
-t $iCEPACKAGE
#constraint file

#options
-optimization_goal Area
-twr_paths 3
-bram_utilization 100.00
-ramstyle Auto
-romstyle Auto
-use_carry_chain 1
-carry_chain_length 0
-resource_sharing 1
-propagate_constants 1
-remove_duplicate_regs 1
-max_fanout 10000
-fsm_encoding_style Auto
-use_io_insertion 1
-use_io_reg auto
-resolve_mixed_drivers 0
-RWCheckOnRam 0
-fix_gated_clocks 1
-loop_limit 1950

-ver "input.v"
-p "$PWD"

#set result format/file last
-output_edif impl/impl.edf

#set log file
-logfile "impl_lse.log"
EOT

# synthesis (Synplify Pro)
if false; then
	"$icecubedir"/sbt_backend/bin/linux/opt/synpwrap/synpwrap -prj impl_syn.prj -log impl.srr
fi

# synthesis (Lattice LSE)
if true; then
	"$icecubedir"/LSE/bin/${lin_lin64}/synthesis -f "impl_lse.prj"
fi

# convert netlist
"$icecubedir"/sbt_backend/bin/linux/opt/edifparser "$icecubedir"/sbt_backend/devices/$devfile "$PWD"/impl/impl.edf "$PWD"/netlist -p$iCEPACKAGE -yinput.pcf -sinput.sdc -c --devicename $iCE40DEV

# run placer
"$icecubedir"/sbt_backend/bin/linux/opt/sbtplacer --des-lib "$PWD"/netlist/oadb-top --outdir "$PWD"/outputs/placer --device-file "$icecubedir"/sbt_backend/devices/$devfile --package $iCEPACKAGE --deviceMarketName $iCE40DEV --sdc-file "$PWD"/Temp/sbt_temp.sdc --lib-file "$icecubedir"/sbt_backend/devices/$libfile --effort_level std --out-sdc-file "$PWD"/outputs/placer/top_pl.sdc

# run packer
"$icecubedir"/sbt_backend/bin/linux/opt/packer "$icecubedir"/sbt_backend/devices/$devfile "$PWD"/netlist/oadb-top --package $iCEPACKAGE --outdir "$PWD"/outputs/packer --translator "$icecubedir"/sbt_backend/bin/sdc_translator.tcl --src_sdc_file "$PWD"/outputs/placer/top_pl.sdc --dst_sdc_file "$PWD"/outputs/packer/top_pk.sdc --devicename $iCE40DEV

# run router
"$icecubedir"/sbt_backend/bin/linux/opt/sbrouter "$icecubedir"/sbt_backend/devices/$devfile "$PWD"/netlist/oadb-top "$icecubedir"/sbt_backend/devices/$libfile "$PWD"/outputs/packer/top_pk.sdc --outdir "$PWD"/outputs/router --sdf_file "$PWD"/outputs/netlist/top_sbt.sdf --pin_permutation

# run netlister
"$icecubedir"/sbt_backend/bin/linux/opt/netlister --verilog "$PWD"/outputs/netlist/top_sbt.v --vhdl "$PWD"/outputs/netlist/top_sbt.vhd --lib "$PWD"/netlist/oadb-top --view rt --device "$icecubedir"/sbt_backend/devices/$devfile --splitio --in-sdc-file "$PWD"/outputs/packer/top_pk.sdc --out-sdc-file "$PWD"/outputs/netlist/top_sbt.sdc

if [ -n "$ICE_SBTIMER_LP" ]; then
	"$icecubedir"/sbt_backend/bin/linux/opt/sbtimer --des-lib "$PWD"/netlist/oadb-top --lib-file "$icecubedir"/sbt_backend/devices/$libfile --sdc-file "$PWD"/outputs/netlist/top_sbt.sdc --sdf-file "$PWD"/outputs/netlist/top_sbt_lp.sdf --report-file "$PWD"/outputs/netlist/top_timing_lp.rpt --device-file "$icecubedir"/sbt_backend/devices/$devfile --timing-summary
fi

# hacks for sbtimer so it knows what device we are dealing with
ln -fs . sbt
ln -fs . foobar_Implmnt
cat > foobar_sbt.project << EOT
[Project]
Implementations=foobar_Implmnt

[foobar_Implmnt]
DeviceFamily=$( echo $iCE40DEV | sed -re 's,(HX|5K|(iCE5LP)).*,\2,'; )
Device=$( echo $iCE40DEV | sed -re 's,(iCE40(UP|LP)?|iCE5LP),,'; )
DevicePackage=$iCEPACKAGE
Devicevoltage=1.14
DevicevoltagePerformance=+/-5%(datasheet default)
DeviceTemperature=85
TimingAnalysisBasedOn=Worst
OperationRange=Commercial
IOBankVoltages=topBank,2.5 bottomBank,2.5 leftBank,2.5 rightBank,2.5
derValue=0.701346
EOT

# run timer
"$icecubedir"/sbt_backend/bin/linux/opt/sbtimer --des-lib "$PWD"/foobar_Implmnt/sbt/netlist/oadb-top --lib-file "$icecubedir"/sbt_backend/devices/$libfile --sdc-file "$PWD"/outputs/netlist/top_sbt.sdc --sdf-file "$PWD"/outputs/netlist/top_sbt.sdf --report-file "$PWD"/outputs/netlist/top_timing.rpt --device-file "$icecubedir"/sbt_backend/devices/$devfile --timing-summary

# make bitmap
"$icecubedir"/sbt_backend/bin/linux/opt/bitmap "$icecubedir"/sbt_backend/devices/$devfile --design "$PWD"/netlist/oadb-top --device_name $iCE40DEV --package $iCEPACKAGE --outdir "$PWD"/outputs/bitmap --debug --low_power on --init_ram on --init_ram_bank 1111 --frequency low --warm_boot on
)

(
set +x
echo "export FOUNDRY=\"$FOUNDRY\""
echo "export SBT_DIR=\"$SBT_DIR\""
echo "export TCL_LIBRARY=\"$TCL_LIBRARY\""
echo "export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH\""
)

cp "$1.tmp"/outputs/bitmap/top_bitmap.bin "$1.bin"
cp "$1.tmp"/outputs/bitmap/top_bitmap_glb.txt "$1.glb"
cp "$1.tmp"/outputs/placer/top_sbt.pcf "$1.psb"
cp "$1.tmp"/outputs/netlist/top_sbt.v "$1.vsb"
cp "$1.tmp"/outputs/netlist/top_sbt.sdf "$1.sdf"
cp "$1.tmp"/outputs/netlist/top_timing.rpt "$1.rpt"
if [ -n "$ICE_SBTIMER_LP" ]; then
	cp "$1.tmp"/outputs/netlist/top_sbt_lp.sdf "$1.slp"
	cp "$1.tmp"/outputs/netlist/top_timing_lp.rpt "$1.rlp"
fi

export LD_LIBRARY_PATH=""
$scriptdir/../icepack/iceunpack "$1.bin" "$1.asc"
