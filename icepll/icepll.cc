//
//  Copyright (C) 2015  Clifford Wolf <clifford@clifford.at>
//
//  Permission to use, copy, modify, and/or distribute this software for any
//  purpose with or without fee is hereby granted, provided that the above
//  copyright notice and this permission notice appear in all copies.
//
//  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
//  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
//  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
//  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
//  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
//  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
//  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
//

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

const char *binstr(int v, int n)
{
	static char buffer[16];
	char *p = buffer;

	for (int i = n-1; i >= 0; i--)
		*(p++) = ((v >> i) & 1) ? '1' : '0';
	*(p++) = 0;

	return buffer;
}

void help(const char *cmd)
{
	printf("\n");
	printf("Usage: %s [options]\n", cmd);
	printf("\n");
	printf("    -i <input_freq_mhz>\n");
	printf("        PLL Input Frequency (default: 12 MHz)\n");
	printf("\n");
	printf("    -o <output_freq_mhz>\n");
	printf("        PLL Output Frequency (default: 60 MHz)\n");
	printf("\n");
	printf("    -S\n");
	printf("        Disable SIMPLE feedback path mode\n");
	printf("\n");
	printf("    -f <filename>\n");
	printf("        Save PLL configuration as Verilog to file\n");
	printf("        If <filename> is - then the Verilog is written to stdout.\n");
	printf("\n");
	printf("    -m\n");
	printf("        Save PLL configuration as Verilog module (May use with -f)\n");
	printf("\n");
	printf("    -n <module name>\n");
	printf("        Specify different Verilog module name than the default 'pll'\n");
	printf("\n");
	printf("    -q\n");
	printf("        Do not print information about the PLL configuration to stdout\n");
	printf("\n");
	exit(1);
}

int main(int argc, char **argv)
{
#ifdef __EMSCRIPTEN__
	EM_ASM(
		if (ENVIRONMENT_IS_NODE)
		{
			FS.mkdir('/hostcwd');
			FS.mount(NODEFS, { root: '.' }, '/hostcwd');
			FS.mkdir('/hostfs');
			FS.mount(NODEFS, { root: '/' }, '/hostfs');
		}
	);
#endif

	double f_pllin = 12;
	double f_pllout = 60;
	bool simple_feedback = true;
	const char* filename = NULL;
	bool file_stdout = false;
	const char* module_name = NULL;
	bool save_as_module = false;
	bool quiet = false;

	int opt;
	while ((opt = getopt(argc, argv, "i:o:Smf:n:q")) != -1)
	{
		switch (opt)
		{
		case 'i':
			f_pllin = atof(optarg);
			break;
		case 'o':
			f_pllout = atof(optarg);
			break;
		case 'S':
			simple_feedback = false;
			break;
		case 'm':
			save_as_module = true;
			break;
		case 'f':
			filename = optarg;
			break;
		case 'n':
			module_name = optarg;
			break;
		case 'q':
			quiet = true;
			break;
		default:
			help(argv[0]);
		}
	}

	if (optind != argc)
		help(argv[0]);

	// Shall save as module, but no filename was given.
	// Write to stdout.
	if (save_as_module && filename == NULL)
		filename = "-";

	// If filename is "-", then use stdout as output stream.
	// That implies quiet mode.
	if (filename != NULL && strcmp(filename, "-") == 0)
	{
		file_stdout = true;
		quiet = true;
	}

	bool found_something = false;
	double best_fout = 0;
	int best_divr = 0;
	int best_divf = 0;
	int best_divq = 0;

	// The documentation in the iCE40 PLL Usage Guide incorrectly lists the
	// maximum value of DIVF as 63, when it is only limited to 63 when using
	// feedback modes other that SIMPLE.
	int divf_max = simple_feedback ? 127 : 63;

	if (f_pllin < 10 || f_pllin > 133) {
		fprintf(stderr, "Error: PLL input frequency %.3f MHz is outside range 10 MHz - 133 MHz!\n", f_pllin);
		exit(1);
	}

	if (f_pllout < 16 || f_pllout > 275) {
		fprintf(stderr, "Error: PLL output frequency %.3f MHz is outside range 16 MHz - 275 MHz!\n", f_pllout);
		exit(1);
	}

	for (int divr = 0; divr <= 15; divr++)
	{
		double f_pfd = f_pllin / (divr + 1);
		if (f_pfd < 10 || f_pfd > 133) continue;

		for (int divf = 0; divf <= divf_max; divf++)
		{
			if (simple_feedback)
			{
				double f_vco = f_pfd * (divf + 1);
				if (f_vco < 533 || f_vco > 1066) continue;

				for (int divq = 1; divq <= 6; divq++)
				{
					double fout = f_vco * exp2(-divq);

					if (fabs(fout - f_pllout) < fabs(best_fout - f_pllout) || !found_something) {
						best_fout = fout;
						best_divr = divr;
						best_divf = divf;
						best_divq = divq;
						found_something = true;
					}
				}
			}
			else
			{
				for (int divq = 1; divq <= 6; divq++)
				{
					double f_vco = f_pfd * (divf + 1) * exp2(divq);
					if (f_vco < 533 || f_vco > 1066) continue;

					double fout = f_vco * exp2(-divq);

					if (fabs(fout - f_pllout) < fabs(best_fout - f_pllout) || !found_something) {
						best_fout = fout;
						best_divr = divr;
						best_divf = divf;
						best_divq = divq;
						found_something = true;
					}
				}
			}
		}
	}

	double f_pfd = f_pllin / (best_divr + 1);;
	double f_vco = f_pfd * (best_divf + 1);

	int filter_range =
			f_pfd < 17 ? 1 :
			f_pfd < 26 ? 2 :
			f_pfd < 44 ? 3 :
			f_pfd < 66 ? 4 :
			f_pfd < 101 ? 5 : 6;

	if (!simple_feedback)
		f_vco *= exp2(best_divq);

	if (!found_something) {
		fprintf(stderr, "Error: No valid configuration found!\n");
		exit(1);
	}

	if (!quiet)
	{
		printf("\n");

		printf("F_PLLIN:  %8.3f MHz (given)\n", f_pllin);
		printf("F_PLLOUT: %8.3f MHz (requested)\n", f_pllout);
		printf("F_PLLOUT: %8.3f MHz (achieved)\n", best_fout);

		printf("\n");

		printf("FEEDBACK: %s\n", simple_feedback ? "SIMPLE" : "NON_SIMPLE");
		printf("F_PFD: %8.3f MHz\n", f_pfd);
		printf("F_VCO: %8.3f MHz\n", f_vco);

		printf("\n");

		printf("DIVR: %2d (4'b%s)\n", best_divr, binstr(best_divr, 4));
		printf("DIVF: %2d (7'b%s)\n", best_divf, binstr(best_divf, 7));
		printf("DIVQ: %2d (3'b%s)\n", best_divq, binstr(best_divq, 3));

		printf("\n");

		printf("FILTER_RANGE: %d (3'b%s)\n", filter_range, binstr(filter_range, 3));

		printf("\n");
	}

	// save PLL configuration as file/stdout.
	if (filename != NULL || file_stdout)
	{
		FILE *f;

		if (file_stdout)
		{
			// use stdout as output stream.
			f = stdout;
		}
		else
		{
			// open file for writing
			f = fopen(filename, "w");
			if (f == NULL)
			{
				fprintf(stderr, "Error: Failed to open output file '%s': %s\n",
					filename, strerror(errno));
				exit(1);
			}
		}

		if (save_as_module)
		{
			// save PLL configuration as Verilog module

			// header
			fprintf(f, "/**\n * PLL configuration\n *\n"
						" * This Verilog module was generated automatically\n"
						" * using the icepll tool from the IceStorm project.\n"
						" * Use at your own risk.\n"
						" *\n"
						" * Given input frequency:      %8.3f MHz\n"
						" * Requested output frequency: %8.3f MHz\n"
						" * Achieved output frequency:  %8.3f MHz\n"
						" */\n\n",
						f_pllin, f_pllout, best_fout);

			// generate Verilog module
			fprintf(f,  "module %s(\n"
						"\tinput  clock_in,\n"
						"\toutput clock_out,\n"
						"\toutput locked\n"
						"\t);\n\n", (module_name ? module_name : "pll")
					);

			// save iCE40 PLL tile configuration
			fprintf(f, "SB_PLL40_CORE #(\n");
			fprintf(f, "\t\t.FEEDBACK_PATH(\"%s\"),\n", (simple_feedback ? "SIMPLE" : "NON_SIMPLE"));
			fprintf(f, "\t\t.DIVR(4'b%s),\t\t"      "// DIVR = %2d\n", binstr(best_divr, 4), best_divr);
			fprintf(f, "\t\t.DIVF(7'b%s),\t"        "// DIVF = %2d\n", binstr(best_divf, 7), best_divf);
			fprintf(f, "\t\t.DIVQ(3'b%s),\t\t"      "// DIVQ = %2d\n", binstr(best_divq, 3), best_divq);
			fprintf(f, "\t\t.FILTER_RANGE(3'b%s)\t" "// FILTER_RANGE = %d\n", binstr(filter_range, 3), filter_range);
			fprintf(f, "\t) uut (\n"
						"\t\t.LOCK(locked),\n"
						"\t\t.RESETB(1'b1),\n"
						"\t\t.BYPASS(1'b0),\n"
						"\t\t.REFERENCECLK(clock_in),\n"
						"\t\t.PLLOUTCORE(clock_out)\n"
						"\t\t);\n\n"
					);

			fprintf(f, "endmodule\n");
		}
		else
		{
			// only save PLL configuration values

			// header
			fprintf(f, "/**\n * PLL configuration\n *\n"
						" * This Verilog header file was generated automatically\n"
						" * using the icepll tool from the IceStorm project.\n"
						" * It is intended for use with FPGA primitives SB_PLL40_CORE,\n"
						" * SB_PLL40_PAD, SB_PLL40_2_PAD, SB_PLL40_2F_CORE or SB_PLL40_2F_PAD.\n"
						" * Use at your own risk.\n"
						" *\n"
						" * Given input frequency:      %8.3f MHz\n"
						" * Requested output frequency: %8.3f MHz\n"
						" * Achieved output frequency:  %8.3f MHz\n"
						" */\n\n",
						f_pllin, f_pllout, best_fout);

			// PLL configuration
			fprintf(f, ".FEEDBACK_PATH(\"%s\"),\n", (simple_feedback ? "SIMPLE" : "NON_SIMPLE"));
			fprintf(f, ".DIVR(4'b%s),\t\t"      "// DIVR = %2d\n", binstr(best_divr, 4), best_divr);
			fprintf(f, ".DIVF(7'b%s),\t"        "// DIVF = %2d\n", binstr(best_divf, 7), best_divf);
			fprintf(f, ".DIVQ(3'b%s),\t\t"      "// DIVQ = %2d\n", binstr(best_divq, 3), best_divq);
			fprintf(f, ".FILTER_RANGE(3'b%s)\t" "// FILTER_RANGE = %d\n", binstr(filter_range, 3), filter_range);
		}

		fclose(f);

		if (!quiet)
			printf("PLL configuration written to: %s\n", filename);
	}

	return 0;
}
