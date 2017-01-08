// This is free and unencumbered software released into the public domain.
//
// Anyone is free to copy, modify, publish, use, compile, sell, or
// distribute this software, either in source code form or as a compiled
// binary, for any purpose, commercial or non-commercial, and by any
// means.

#include "libiceuncompr.c"

void help()
{
	printf("\n");
	printf("Usage: iceuncompr [input-file [output-file]]\n");
	printf("\n");
	exit(1);
}

int main(int argc, char **argv)
{
	input_file = stdin;
	output_file = stdout;

	int opt;
	while ((opt = getopt(argc, argv, "v")) != -1)
	{
		switch (opt)
		{
		case 'v':
			break;
		default:
			help();
		}
	}

	if (optind < argc) {
		input_file = fopen(argv[optind], "rb");
		if (input_file == NULL) {
			fprintf(stderr, "Failed to open input file `%s': %s\n", argv[optind], strerror(errno));
			return 1;
		}
		optind++;
	}

	if (optind < argc) {
		output_file = fopen(argv[optind], "wb");
		if (output_file == NULL) {
			fprintf(stderr, "Failed to open output file `%s': %s\n", argv[optind], strerror(errno));
			return 1;
		}
		optind++;
	}

	if (optind != argc)
		help();

	if (optind != argc)
		help();

	return ice_uncompress();
}

