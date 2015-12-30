# OSX Install
The toolchain should be easy to install on OSX platforms. Below are a few troubleshooting items found on Mountain Lion (10.8.2). 

## installing ftdi library
- libftdi (allows you to have .so lib binary and the ftdi.h header)
libftdi has been renamed to libftdi0, so either do:

`port install libftdi0` (note that ports installs the tool to /opt instead of /usr, see next note)

`brew install libftdi0`

## iceprog make error on "ftdi.h not found"
Note that Mac Ports installs to /opt instead of /usr, so change the makefile's first two lines to:

`  LDLIBS = -L/usr/local/lib -L/opt/local/lib -lftdi -lm`

`  CFLAGS = -MD -O0 -ggdb -Wall -std=c99 -I/usr/local/include -I/opt/local/include/`

Basically you are indicating where to find the lib with -L/opt/local/lib and where to find the .h with -I/opt/local/include/

## yosis make error on "<tuple> not found"
This is a compiler issue, i.e., you are probably running on clang and you can circumvent this error by compiling against another compiler.
Edit the Makefile of yosis and replace the two first lines for this, i.e., comment the first line (clang) and uncomment the second (gcc):

`#CONFIG := clang`

` CONFIG := gcc`

##  error "Can't find iCE FTDI USB device (vedor_id 0x0403, device_id 0x6010)." while uploading code to FPGA (e.g., `iceprog example.bin`)
You need to unload the FTDI driver. (notes below are from Mountain Lion, 10.8.2).
First check if it is running: `kextstat | grep FTDIUSBSerialDriver`

If you see if on the kextstat, we need to unload it: `sudo kextunload -b com.FTDI.driver.FTDIUSBSerialDriver`

Repeat the kextstat command and check that the driver was successfully unloaded. 

Repeat your `iceprog example.bin`

Note: On newer OSes perhaps you need to also kextunload the `com.apple.driver.AppleUSBFTDI`
