#ifndef FTDI_INTERFACE_H
#define FTDI_INTERFACE_H

#include <stdint.h>
#include <stdbool.h>
#include "interface.h"


extern const interface_t ftdi_interface;

void ftdi_interface_init(int ifnum, const char *devstr, bool slow_clock);

#endif
