Notes for Installing on OSX
===========================

The toolchain should be easy to install on OSX platforms. Below are a
few troubleshooting items found on Mountain Lion (10.8.2).

See https://github.com/ddm/icetools for a set of shell scripts to build
IceStorm on OSX (using brew for dependencies).

Installing FTDI Library
-----------------------

The libftdi package (.so lib binary and the ftdi.h header) has been
renamed to libftdi0, so either do:

| ``port install libftdi0``
| (note that ports installs the tool to /opt instead of /usr, see
   next note)

``brew install libftdi0``

iceprog make error on "ftdi.h not found"
----------------------------------------

Note that Mac Ports installs to /opt instead of /usr, so change the
first two lines in ``iceprog/Makefile`` to:

::

   LDLIBS = -L/usr/local/lib -L/opt/local/lib -lftdi -lm
   CFLAGS = -MD -O0 -ggdb -Wall -std=c99 -I/usr/local/include -I/opt/local/include/

Basically you are indicating where to find the lib with
``-L/opt/local/lib`` and where to find the .h with
``-I/opt/local/include/``.

yosys make error on "<tuple> not found"
---------------------------------------

This is a compiler issue, i.e., you are probably running on clang and
you can circumvent this error by compiling against another compiler.
Edit the Makefile of yosys and replace the two first lines for this,
i.e., comment the first line (clang) and uncomment the second (gcc):

::

   #CONFIG := clang
   CONFIG := gcc

error "Can't find iCE FTDI USB device (vendor_id 0x0403, device_id 0x6010)." while uploading code to FPGA (e.g., "iceprog example.bin")
---------------------------------------------------------------------------------------------------------------------------------------

You need to unload the FTDI driver (notes below are from Mountain Lion,
10.8.2). First check if it is running:

::

   kextstat | grep FTDIUSBSerialDriver

If you see it on the kextstat, we need to unload it:

::

   sudo kextunload -b com.FTDI.driver.FTDIUSBSerialDriver

Repeat the ``kextstat`` command and check that the driver was
successfully unloaded.

Try running ``iceprog example.bin`` again. It should be working now.

Note: On newer OSes perhaps you need to also kextunload the
``com.apple.driver.AppleUSBFTDI`` driver.
