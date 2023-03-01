#include "rpi_pico_interface.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/time.h>
#include <libusb-1.0/libusb.h>

#define VENDOR_ID 0xCAFE
#define PRODUCT_ID 0x4010

//static hid_device * handle;

libusb_context *ctx=NULL;
struct libusb_device_handle *devhaccess;

int read_calls = 0;
int write_calls = 0;
float read_time = 0;
float write_time = 0;

typedef struct {
    struct timeval start_time;
    struct timeval stop_time;
} time_event_t;

void time_event_start(struct timeval* start_time) {
    gettimeofday(start_time, NULL);
}

float time_event_finish(struct timeval* start_time) {
    struct timeval stop_time;
    gettimeofday(&stop_time, NULL);

    return stop_time.tv_sec + stop_time.tv_usec/1000000.0 - start_time->tv_sec - start_time->tv_usec/1000000.0;
}

// https://github.com/jerome-labidurie/avr/blob/master/fpusb/host-libusb/fpusb.c
void usb_exit ( int sig )
{
   libusb_release_interface (devhaccess, 0);
   libusb_close (devhaccess);
   libusb_exit (ctx);
   exit(sig);

}

int usb_write(uint8_t request, uint8_t* data, int length) {
    struct timeval start_time;
    time_event_start(&start_time);

   int ret = libusb_control_transfer ( devhaccess,
                                   0x40,
                                   request,
                                   0,
                                   0,
                                   data,
                                   length,
                                   1000);

    write_calls++;
    write_time += time_event_finish(&start_time);
    return ret;
}

int usb_read(uint8_t request, uint8_t* data, int length) {
    struct timeval start_time;
    time_event_start(&start_time);

   int ret = libusb_control_transfer ( devhaccess,
                                   0xC0,
                                   request,
                                   0,
                                   0,
                                   data,
                                   length,
                                   1000);

    read_calls++;
    read_time += time_event_finish(&start_time);
    return ret;
}

typedef enum
{
    FLASHER_REQUEST_PIN_DIRECTION_SET = 0x10,       // Configurure GPIO pin directions
    FLASHER_REQUEST_PULLUPS_SET = 0x12,             // Configure GPIO pullups
    FLASHER_REQUEST_PIN_VALUES_SET = 0x20,          // Set GPIO output values
    FLASHER_REQUEST_PIN_VALUES_GET = 0x30,          // Get GPIO input values
    FLASHER_REQUEST_SPI_BITBANG_CS = 0x41,          // SPI transaction with CS pin
    FLASHER_REQUEST_SPI_BITBANG_NO_CS = 0x42,       // SPI transaction without CS pin
    FLASHER_REQUEST_SPI_PINS_SET = 0x43,            // Configure SPI pins
    FLASHER_REQUEST_ADC_READ = 0x50,                // Read ADC inputs
    FLASHER_REQUEST_BOOTLOADER = 0xFF               // Jump to bootloader mode
} flasher_request_t;

static void pin_set_direction(uint8_t pin, bool direction) {
    const uint32_t mask = (1<<pin);
    const uint32_t val = ((direction?1:0)<<pin);

    uint8_t buf[8];
    buf[0] = (mask >> 24) & 0xff;
    buf[1] = (mask >> 16) & 0xff;
    buf[2] = (mask >> 8) & 0xff;
    buf[3] = (mask >> 0) & 0xff;
    buf[4] = (val >> 24) & 0xff;
    buf[5] = (val >> 16) & 0xff;
    buf[6] = (val >> 8) & 0xff;
    buf[7] = (val >> 0) & 0xff;

    usb_write(FLASHER_REQUEST_PIN_DIRECTION_SET, buf, sizeof(buf));
}

static void pinmask_write(uint32_t mask, uint32_t val) {
    uint8_t buf[8];
    buf[0] = (mask >> 24) & 0xff;
    buf[1] = (mask >> 16) & 0xff;
    buf[2] = (mask >> 8) & 0xff;
    buf[3] = (mask >> 0) & 0xff;
    buf[4] = (val >> 24) & 0xff;
    buf[5] = (val >> 16) & 0xff;
    buf[6] = (val >> 8) & 0xff;
    buf[7] = (val >> 0) & 0xff;

//    printf("pin_write [");
//    for(int i = 0; i < sizeof(buf); i++) {
//        printf("%02x, ", buf[i]);
//    }
//    printf("]\n");

    usb_write(FLASHER_REQUEST_PIN_VALUES_SET, buf, sizeof(buf));
}

static void pin_write(uint8_t pin, bool value) {
    const uint32_t mask = (1<<pin);
    const uint32_t val = ((value?1:0)<<pin);

    pinmask_write(mask, val);
}

static bool pin_read(uint8_t pin) {
    uint8_t ret_buf[4];
    usb_read(FLASHER_REQUEST_PIN_VALUES_GET, ret_buf, sizeof(ret_buf));

//    printf("  ret=[");
//    for(int i = 0; i < sizeof(ret_buf); i++) {
//        printf("%02x, ", ret_buf[i]);
//    }
//    printf("]\n");

    uint32_t pins =
        (ret_buf[0] << 24)
        | (ret_buf[1] << 16)
        | (ret_buf[2] << 8)
        | (ret_buf[3] << 0);

    return (pins & (1<<pin));
}

static void set_spi_pins(
    uint8_t sck_pin,
    uint8_t cs_pin,
    uint8_t mosi_pin,
    uint8_t miso_pin) {

    uint8_t buf[4];
    buf[0] = sck_pin;
    buf[1] = cs_pin;
    buf[2] = mosi_pin;
    buf[3] = miso_pin;

    usb_write(FLASHER_REQUEST_SPI_PINS_SET, buf, sizeof(buf));
}

//#define MAX_BYTES_PER_TRANSFER (256-7)
#define MAX_BYTES_PER_TRANSFER (1024-8)


static void bitbang_spi_no_cs(
    uint32_t bit_count,
    uint8_t* buf_out,
    uint8_t* buf_in) {

    const uint32_t byte_count = ((bit_count + 7) / 8);
    if(byte_count > MAX_BYTES_PER_TRANSFER) {
        printf("bit count too high\n");
        exit(1);
    }

    uint8_t buf[4+MAX_BYTES_PER_TRANSFER];
    memset(buf, 0xFF, sizeof(buf));

    buf[0] = (bit_count >> 24) & 0xff;
    buf[1] = (bit_count >> 16) & 0xff;
    buf[2] = (bit_count >> 8) & 0xff;
    buf[3] = (bit_count >> 0) & 0xff;

    memcpy(&buf[4], buf_out, byte_count);

    usb_write(FLASHER_REQUEST_SPI_BITBANG_NO_CS, buf, byte_count+4);

    if(buf_in != NULL) {
        usb_read(FLASHER_REQUEST_SPI_BITBANG_NO_CS, buf_in, byte_count);
    }
}

#define PIN_POWER 7
#define PIN_SCK 10
#define PIN_MOSI 13
#define PIN_SS 12
#define PIN_MISO 11
#define PIN_CRESET 14
#define PIN_CDONE 15

// ********* iceprog API ****************

// TODO
static void close() {
//    pin_set_direction(PIN_POWER, true);
    pin_set_direction(PIN_SCK, false);
    pin_set_direction(PIN_MOSI, false);
    pin_set_direction(PIN_SS, false);
    pin_set_direction(PIN_MISO, false);
    pin_set_direction(PIN_CRESET, false);
    pin_set_direction(PIN_CDONE, false);

    printf("closing\n");

   libusb_release_interface (devhaccess, 0);
   libusb_close (devhaccess);
   libusb_exit (ctx);

    printf("Done\n  read time:%f\n  write time:%f\n  read calls:%i\n  write calls:%i\n", read_time, write_time, read_calls, write_calls);
}

// TODO
static void error(int status) {
    close();
    exit(status);
}

// TODO
static void set_cs_creset(int cs_b, int creset_b) {
    pinmask_write(
        (1<<PIN_SS) | (1<PIN_CRESET),
        ((cs_b>0?1:0)<<PIN_SS) | ((creset_b>0?1:0)<<PIN_CRESET)
    );
}

// TODO
static bool get_cdone(void) { 
    return pin_read(PIN_CDONE);
}

// TODO
static uint8_t xfer_spi_bits(uint8_t data, int n) {
    uint8_t buf = data;
    bitbang_spi_no_cs(n, &buf, &buf);

    return buf;
}

// TODO
static void xfer_spi(uint8_t *data, int n) {
    bitbang_spi_no_cs(n*8, data, data);
}

// TODO
static void send_spi(uint8_t *data, int n) {
    bitbang_spi_no_cs(n*8, data, NULL);
}

// TODO
static void send_dummy_bytes(uint8_t n) {
    uint8_t buf[n];
    memset(buf, 0, sizeof(buf));
    send_spi(buf, sizeof(buf));
}


// TODO
static void send_dummy_bit(void) {
    uint8_t buf = 0;
    bitbang_spi_no_cs(1, &buf, NULL);
}


const interface_t rpi_pico_interface = {
	.close = close,
	.error = error,

	.set_cs_creset = set_cs_creset,
	.get_cdone = get_cdone,

	.send_spi = send_spi,
	.xfer_spi = xfer_spi,
	.xfer_spi_bits = xfer_spi_bits,

	.send_dummy_bytes = send_dummy_bytes,
	.send_dummy_bit = send_dummy_bit,
};

bool check_for_old_firmware() {
    const int vendor_id_old = 0xCAFE;
    const int product_id_old = 0x4004;

    if ( (devhaccess = libusb_open_device_with_vid_pid (ctx, vendor_id_old, product_id_old)) == 0) {
        return false;
    }

    libusb_close (devhaccess);
    return true;
}

void rpi_pico_interface_init() {
    if (libusb_init(&ctx) != 0) {
        printf("failure!\n");

        exit(-1);
    }

    if ( (devhaccess = libusb_open_device_with_vid_pid (ctx, VENDOR_ID, PRODUCT_ID)) == 0) {
        if(check_for_old_firmware()) {
            printf("Programmer with incompatible firmware detected- please update to the latest version!\n");
            printf("See: https://github.com/tillitis/tillitis-key1/blob/main/doc/toolchain_setup.md#fw-update-of-programmer-board\n");
        }
        else {
            printf("libusb_open_device_with_vid_pid error\n");
        }
        libusb_exit(ctx);
        exit(-1);
    }

    if (libusb_claim_interface (devhaccess, 0) != 0) {
        perror ("libusb_claim_interface error");
        usb_exit(-1);
    }

    printf("This iceprog has raw power!\n");

    pin_set_direction(PIN_POWER, true);
    pin_set_direction(PIN_SCK, true);
    pin_set_direction(PIN_MOSI, true);
    pin_set_direction(PIN_SS, true);
    pin_set_direction(PIN_MISO, false);
    pin_set_direction(PIN_CRESET, true);
    pin_set_direction(PIN_CDONE, false);

    pin_write(PIN_POWER, true);

    set_spi_pins(PIN_SCK, PIN_SS, PIN_MOSI, PIN_MISO);
}

// ********* API ****************
