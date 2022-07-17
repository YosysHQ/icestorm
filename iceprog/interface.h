#ifndef INTERFACE_H
#define INTERFACE_H

// Interface
typedef struct {
	void (*close)(void);
	void (*error)(int status);

	void (*set_cs_creset)(int cs_b, int creset_b);
	bool (*get_cdone)(void);

	void (*send_spi)(uint8_t *data, int n);
	void (*xfer_spi)(uint8_t *data, int n);
	uint8_t (*xfer_spi_bits)(uint8_t data, int n);
	void (*send_dummy_bytes)(uint8_t n);  // probably remvoe this
	void (*send_dummy_bit)(void); // probably remove this
} interface_t;

#endif
