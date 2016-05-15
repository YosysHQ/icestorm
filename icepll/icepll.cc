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
#include <unistd.h>
#include <string.h>
#include <math.h>

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
	exit(1);
}

int main(int argc, char **argv)
{
	double f_pllin = 12;
	double f_pllout = 60;
	bool simple_feedback = true;

	int opt;
	while ((opt = getopt(argc, argv, "i:o:S")) != -1)
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
		default:
			help(argv[0]);
		}
	}

	if (optind != argc)
		help(argv[0]);

	bool found_something = false;
	double best_fout = 0;
	int best_divr = 0;
	int best_divf = 0;
	int best_divq = 0;

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

		for (int divf = 0; divf <= 127; divf++)
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

	return 0;
}
