//
//  Copyright (C) 2015  Marcus Comstedt <marcus@mc.pp.se>
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

#include <fstream>
#include <iostream>
#include <cstdint>
#include <memory>

#include <err.h>
#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>

#define info(...) do { if (log_level > 0) fprintf(stderr, __VA_ARGS__); } while (0)

int log_level = 0;

static const int NUM_IMAGES = 4;
static const int NUM_HEADERS = NUM_IMAGES + 1;
static const int HEADER_SIZE = 32;

static void align_offset(uint32_t &offset, int bits)
{
    uint32_t mask = (1 << bits) - 1;
    if (offset & mask)
        offset = (offset | mask) + 1;
}

static void write_byte(std::ostream &ofs, uint32_t &file_offset, uint8_t byte)
{
    ofs << byte;
    file_offset++;
}

static void write_bytes(std::ostream &ofs, uint32_t &file_offset,
                        const uint8_t *buf, size_t n)
{
    if (n > 0) {
        ofs.write(reinterpret_cast<const char*>(buf), n);
        file_offset += n;
    }
}

static void write_file(std::ostream &ofs, uint32_t &file_offset,
                       std::istream &ifs, const char *filename)
{
    const size_t bufsize = 8192;
    uint8_t *buffer = new uint8_t[bufsize];

    while(!ifs.eof()) {
        ifs.read(reinterpret_cast<char *>(buffer), bufsize);
        if (ifs.bad())
            err(EXIT_FAILURE, "can't read input image `%s'", filename);
        write_bytes(ofs, file_offset, buffer, ifs.gcount());
    }

    delete[] buffer;
}

static void pad_to(std::ostream &ofs, uint32_t &file_offset, uint32_t target)
{
    if (target < file_offset)
        errx(EXIT_FAILURE, "trying to pad backwards");
    while(file_offset < target)
        write_byte(ofs, file_offset, 0xff);
}

class Image {
    const char *filename;
    std::ifstream ifs;
    uint32_t offs;

public:
    Image(const char *filename);
    size_t size();
    void write(std::ostream &ofs, uint32_t &file_offset);
    void place(uint32_t o) { offs = o; }
    uint32_t offset() const { return offs; }
};

Image::Image(const char *filename) : filename(filename), ifs(filename, std::ifstream::binary)
{
    if (ifs.fail())
        err(EXIT_FAILURE, "can't open input image `%s'", filename);
}

size_t Image::size()
{
    ifs.seekg (0, ifs.end);
    if (ifs.fail())
        err(EXIT_FAILURE, "can't seek on input image `%s'", filename);
    size_t length = ifs.tellg();
    ifs.seekg (0, ifs.beg);
    if (ifs.fail())
        err(EXIT_FAILURE, "can't seek on input image `%s'", filename);

    if (length == 0)
        errx(EXIT_FAILURE, "input image `%s' doesn't contain any data", filename);
    return length;
}

void Image::write(std::ostream &ofs, uint32_t &file_offset)
{
    write_file(ofs, file_offset, ifs, filename);
}

static void write_header(std::ostream &ofs, uint32_t &file_offset,
                         Image const *image, bool coldboot)
{
    // Preamble
    write_byte(ofs, file_offset, 0x7e);
    write_byte(ofs, file_offset, 0xaa);
    write_byte(ofs, file_offset, 0x99);
    write_byte(ofs, file_offset, 0x7e);

    // Boot mode
    write_byte(ofs, file_offset, 0x92);
    write_byte(ofs, file_offset, 0x00);
    write_byte(ofs, file_offset, coldboot ? 0x10 : 0x00);

    // Boot address
    write_byte(ofs, file_offset, 0x44);
    write_byte(ofs, file_offset, 0x03);
    write_byte(ofs, file_offset, (image->offset() >> 16) & 0xff);
    write_byte(ofs, file_offset, (image->offset() >> 8) & 0xff);
    write_byte(ofs, file_offset, image->offset() & 0xff);

    // Bank offset
    write_byte(ofs, file_offset, 0x82);
    write_byte(ofs, file_offset, 0x00);
    write_byte(ofs, file_offset, 0x00);

    // Reboot
    write_byte(ofs, file_offset, 0x01);
    write_byte(ofs, file_offset, 0x08);

    // Zero out any unused bytes
    while (file_offset & (HEADER_SIZE - 1))
        write_byte(ofs, file_offset, 0x00);
}

void usage(const char *program_name)
{
    fprintf(stderr, "Create a multi-configuration image from up to four configuration images.\n");
    fprintf(stderr, "Usage: %s [OPTION]... INPUT-FILE...\n", program_name);
    fprintf(stderr, "\n");
    fprintf(stderr, "  -c                    coldboot mode: image loaded on power-on or after a low\n");
    fprintf(stderr, "                          pulse on CRESET_B is determined by the value of the\n");
    fprintf(stderr, "                          pins CBSEL0 and CBSEL1\n");
    fprintf(stderr, "  -p0, -p1, -p2, -p3    specifies image to be loaded on power-on or after a low\n");
    fprintf(stderr, "                          pulse on CRESET_B (not applicable in coldboot mode)\n");
    fprintf(stderr, "  -a N                  align images at 2^N bytes\n");
    fprintf(stderr, "  -A N                  like `-a N', but align the first image, too\n");
    fprintf(stderr, "  -o OUTPUT-FILE        write output to OUTPUT-FILE instead of stdout\n");
    fprintf(stderr, "  -v                    print image offsets to stderr\n");
    fprintf(stderr, "      --help            display this help and exit\n");
    fprintf(stderr, "\n");
    fprintf(stderr, "If you have a bug report, please file an issue on github:\n");
    fprintf(stderr, "  https://github.com/cliffordwolf/icestorm/issues\n");
}

int main(int argc, char **argv)
{
    int c;
    char *endptr = NULL;
    bool coldboot = false;
    int por_image = 0;
    int header_count = 0;
    int image_count = 0;
    int align_bits = 0;
    bool align_first = false;
    Image *header_images[NUM_HEADERS];
    std::unique_ptr<Image> images[NUM_IMAGES];
    const char *outfile_name = NULL;

    static struct option long_options[] = {
        {"help", no_argument, NULL, -2},
        {NULL, 0, NULL, 0}
    };

    while ((c = getopt_long(argc, argv, "cp:a:A:o:v",
                long_options, NULL)) != -1)
        switch (c) {
            case 'c':
                coldboot = true;
                break;
            case 'p':
                if (optarg[0] == '0' && optarg[1] == '\0')
                    por_image = 0;
                else if (optarg[0] == '1' && optarg[1] == '\0')
                    por_image = 1;
                else if (optarg[0] == '2' && optarg[1] == '\0')
                    por_image = 2;
                else if (optarg[0] == '3' && optarg[1] == '\0')
                    por_image = 3;
                else
                    errx(EXIT_FAILURE, "`%s' is not a valid power-on/reset image (must be 0, 1, 2, or 3)", optarg);
                break;
            case 'A':
                align_first = true;
                /* fallthrough */
            case 'a':
                align_bits = strtol(optarg, &endptr, 0);
                if (*endptr != '\0')
                    errx(EXIT_FAILURE, "`%s' is not a valid number", optarg);
                if (align_bits < 0)
                    errx(EXIT_FAILURE, "argument to `-%c' must be non-negative", c);
                break;
            case 'o':
                outfile_name = optarg;
                break;
            case 'v':
                log_level++;
                break;
            case -2:
                usage(argv[0]);
                exit(EXIT_SUCCESS);
            default:
                fprintf(stderr, "Try `%s --help' for more information.\n", argv[0]);
                return EXIT_FAILURE;
        }

    if (optind == argc) {
        warnx("missing argument");
        fprintf(stderr, "Try `%s --help' for more information.\n", argv[0]);
        return EXIT_FAILURE;
    }

    while (optind != argc) {
        if (header_count >= NUM_IMAGES)
            errx(EXIT_FAILURE, "too many images supplied (maximum is 4)");
        images[image_count].reset(new Image(argv[optind++]));
        header_images[header_count + 1] = &*images[image_count];
        header_count++;
        image_count++;
    }

    if (coldboot && por_image != 0)
        errx(EXIT_FAILURE, "can't select power-on/reset boot image in cold boot mode");

    if (por_image >= header_count)
        errx(EXIT_FAILURE, "specified non-existing image for power-on/reset");

    // Place images
    uint32_t offs = NUM_HEADERS * HEADER_SIZE;
    if (align_first)
        align_offset(offs, align_bits);
    for (int i=0; i<image_count; i++) {
        images[i]->place(offs);
        offs += images[i]->size();
        align_offset(offs, align_bits);
        info("Place image %d at %06x .. %06x.\n", i, int(images[i]->offset()), int(offs));
    }

    // Populate headers
    header_images[0] = header_images[por_image + 1];
    for (int i=header_count; i < NUM_IMAGES; i++)
        header_images[i + 1] = header_images[0];

    std::ofstream ofs;
    std::ostream *osp;

    if (outfile_name != NULL) {
        ofs.open(outfile_name, std::ofstream::binary);
        if (!ofs.is_open())
            err(EXIT_FAILURE, "can't open output file `%s'", outfile_name);
        osp = &ofs;
    } else {
        osp = &std::cout;
    }

    uint32_t file_offset = 0;
    for (int i=0; i<NUM_HEADERS; i++)
    {
        pad_to(*osp, file_offset, i * HEADER_SIZE);
        write_header(*osp, file_offset, header_images[i], i == 0 && coldboot);
    }
    for (int i=0; i<image_count; i++)
    {
        pad_to(*osp, file_offset, images[i]->offset());
        images[i]->write(*osp, file_offset);
    }

    info("Done.\n");
    return EXIT_SUCCESS;
}
