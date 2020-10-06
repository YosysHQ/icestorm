/*
 *  icebin2nvcm -- tool to generate .nvcm file from iCE40 family .bin file
 *
 *  Copyright (C) 2020 Peter Lawrence
 *
 *  Permission to use, copy, modify, and/or distribute this software for any
 *  purpose with or without fee is hereby granted, provided that the above
 *  copyright notice and this permission notice appear in all copies.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 *  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 *  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 *  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 *  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 *  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 *  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#include <stdint.h>
#include <stdio.h>
#include <malloc.h>
#include <string.h>

int main(int argc, char *argv[])
{
	FILE *input, *output;
	int pos, origin = -1;
	int nvcm_addr;
	const uint8_t zeros[8] = { 0, 0, 0, 0, 0, 0, 0, 0 };
	uint8_t data[sizeof(zeros)];
	int len;
	uint32_t preamble;
	char *header;
	const char *device_name = NULL, *part_type = NULL;

	if (argc < 3)
	{
		fprintf(stderr, "%s <bin_file> <nvcm_file>\n", argv[0]);
		return -3;
	}

	/* look for preamble signature in .bin file */

	input = fopen(argv[1], "rb");

	if (!input) return -1;

	for (pos = 1, preamble = 0; ; pos++)
	{
		int byte = fgetc(input);
		if (byte < 0) break;

		preamble = (preamble << 8) | byte;

		if (0x7EAA997E == preamble)
		{
			origin = pos - 4;
		}
	}

	if (origin < 0)
	{
		fprintf(stderr, "ERROR: unable to find signature in .bin file (%s)\n", argv[1]);
		return -4;
	}

	/* load comment header into RAM to mine for metadata */

	header = (char *)malloc(origin + 1 /* extra byte for NUL terminator */);

	if (!header)
	{
		fprintf(stderr, "ERROR: unable to malloc memory for header\n");
		return -5;
	}

	rewind(input);
	if (origin != fread(header, 1, origin, input))
	{
		fprintf(stderr, "ERROR: unable to read .bin header\n");
		return -6;
	}
	header[origin] = '\0'; /* hopefully extra NUL terminator */

	/* parse comments, searching for the metadata that we need */

	for (int i = 0; i < origin; i += len + 1)
	{
		len = strlen(header + i);
		if (!len) break;

		char *pnt = strstr(header + i, "Part: ");
		if (pnt)
		{
			device_name = header + i + 6;
			pnt = strchr(device_name, '-');
			if (pnt)
			{
				part_type = pnt + 1;
				*pnt = '\0';
			}
			break;
		}
	}

	output = fopen(argv[2], "wb");

	if (!output) return -2;

	if (device_name) fprintf(output, "#DN %s\n", device_name);
	if (part_type) fprintf(output, "#PT %s\n", part_type);

	fprintf(output, "06\n"); /* write enable */

	for (pos = 0; ; pos += sizeof(zeros))
	{
		memset(data, 0, sizeof(data));
		len = fread(data, 1, sizeof(data), input);
		
		/* .nvcm only contains blocks with non-zeros */
		if (memcmp(data, zeros, sizeof(zeros)))
		{
			/* translate .bin address into NVCM address */
			nvcm_addr  = (pos / 328) * 4096 + (pos % 328);

			/* page program */
			fprintf(output, "02 %02x %02x %02x ", (uint8_t)(nvcm_addr >> 16), (uint8_t)(nvcm_addr >> 8), (uint8_t)(nvcm_addr >> 0));
			for (int i = 0; i < sizeof(zeros); i++) fprintf(output, "%02x ", data[i]);
			fprintf(output, "\n");
		}

		if (len < sizeof(data)) break;
	}

	fprintf(output, "04\n"); /* write disable */
	fclose(output);

	free(header);
	fclose(input);
}
