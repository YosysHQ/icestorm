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
	ice40_compr_input_file = stdin;
	ice40_uncompr_output_file = stdout;

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
		ice40_compr_input_file = fopen(argv[optind], "rb");
		if (ice40_compr_input_file == NULL) {
			fprintf(stderr, "Failed to open input file `%s': %s\n", argv[optind], strerror(errno));
			return 1;
		}
		optind++;
	}

	if (optind < argc) {
		ice40_uncompr_output_file = fopen(argv[optind], "wb");
		if (ice40_uncompr_output_file == NULL) {
			fprintf(stderr, "Failed to open output file `%s': %s\n", argv[optind], strerror(errno));
			return 1;
		}
		optind++;
	}

	if (optind != argc)
		help();

	if (optind != argc)
		help();

	return ice40_uncompress();
}

