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

#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

#define log(...) fprintf(stderr, __VA_ARGS__);
#define error(...) do { fprintf(stderr, "%s: ", program_short_name); fprintf(stderr, __VA_ARGS__); exit(EXIT_FAILURE); } while (0)

static char *program_short_name;

static const int NUM_IMAGES = 4;
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
            error("can't read input image `%s': %s\n", filename, strerror(errno));
        write_bytes(ofs, file_offset, buffer, ifs.gcount());
    }

    delete[] buffer;
}

static void pad_to(std::ostream &ofs, uint32_t &file_offset, uint32_t target)
{
    if (target < file_offset)
        error("Trying to pad backwards!\n");
    while(file_offset < target)
        write_byte(ofs, file_offset, 0xff);
}

class Image {
    std::ifstream ifs;
    uint32_t offs;

public:
    const char *const filename;

    Image(const char *filename);
    size_t size();
    void write(std::ostream &ofs, uint32_t &file_offset);
    void place(uint32_t o) { offs = o; }
    uint32_t offset() const { return offs; }
};

Image::Image(const char *filename) : ifs(filename, std::ifstream::binary), filename(filename)
{
    if (ifs.fail())
        error("can't open input image `%s': %s\n", filename, strerror(errno));
}

size_t Image::size()
{
    ifs.seekg (0, ifs.end);
    if (ifs.fail())
        error("can't seek on input image `%s': %s\n", filename, strerror(errno));
    size_t length = ifs.tellg();
    ifs.seekg (0, ifs.beg);
    if (ifs.fail())
        error("can't seek on input image `%s': %s\n", filename, strerror(errno));

    if (length == 0)
        error("input image `%s' doesn't contain any data\n", filename);
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

void usage(const char *cmd)
{
    log("\n");
    log("Usage: %s [options] input-files\n", cmd);
    log("\n");
    log(" -c\n");
    log(" coldboot mode, power on reset image is selected by CBSEL0/CBSEL1\n");
    log("\n");
    log(" -p0, -p1, -p2, -p3\n");
    log(" select power on reset image when not using coldboot mode\n");
    log("\n");
    log(" -a<n>, -A<n>\n");
    log(" align images at 2^<n> bytes. -A also aligns image 0.\n");
    log("\n");
    log(" -o filename\n");
    log(" write output image to file instead of stdout\n");
    log("\n");
    log(" -v\n");
    log(" verbose (repeat to increase verbosity)\n");
    log("\n");
    exit(EXIT_FAILURE);
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

    int c;
    char *endptr = NULL;
    bool coldboot = false;
    int por_image = 0;
    int header_count = 0;
    int image_count = 0;
    int align_bits = 0;
    bool align_first = false;
    Image *header_images[NUM_IMAGES];
    std::unique_ptr<Image> images[NUM_IMAGES];
    const char *outfile_name = NULL;
    bool print_offsets = false;

    static struct option long_options[] = {
        {NULL, 0, NULL, 0}
    };

    program_short_name = strrchr(argv[0], '/');
    if (program_short_name == NULL)
        program_short_name = argv[0];
    else
        program_short_name++;

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
                    error("`%s' is not a valid power-on/reset image (must be 0, 1, 2, or 3)\n", optarg);
                break;
            case 'A':
                align_first = true;
                /* fallthrough */
            case 'a':
                align_bits = strtol(optarg, &endptr, 0);
                if (*endptr != '\0')
                    error("`%s' is not a valid number\n", optarg);
                if (align_bits < 0)
                    error("argument to `-%c' must be non-negative\n", c);
                break;
            case 'o':
                outfile_name = optarg;
                break;
            case 'v':
                print_offsets = true;
                break;
            default:
                usage(argv[0]);
        }

    if (optind == argc) {
        fprintf(stderr, "%s: missing argument\n", program_short_name);
        usage(argv[0]);
    }

    while (optind != argc) {
        if (header_count >= NUM_IMAGES)
            error("Too many images supplied\n");
        for (int i = 0; i < image_count; i++)
            if (strcmp(argv[optind], images[i]->filename) == 0) {
                header_images[header_count] = &*images[i];
                goto image_found;
            }
        images[image_count].reset(new Image(argv[optind]));
        header_images[header_count] = &*images[image_count];
        image_count++;

    image_found:
        header_count++;
        optind++;
    }

    if (coldboot && por_image != 0)
        error("Can't select power on reset boot image in cold boot mode\n");

    if (por_image >= header_count)
        error("Specified non-existing image for power on reset\n");

    // Place images
    uint32_t offs = (NUM_IMAGES + 1) * HEADER_SIZE;
    if (align_first)
        align_offset(offs, align_bits);
    for (int i=0; i<image_count; i++) {
        images[i]->place(offs);
        offs += images[i]->size();
        align_offset(offs, align_bits);
        if (print_offsets)
            fprintf(stderr, "Place image %d at %06x .. %06x (`%s')\n", i, int(images[i]->offset()), int(offs), images[i]->filename);
    }

    // Populate headers
    for (int i=header_count; i < NUM_IMAGES; i++)
        header_images[i] = header_images[por_image];

    std::ofstream ofs;
    std::ostream *osp;

    if (outfile_name != NULL) {
        ofs.open(outfile_name, std::ofstream::binary);
        if (!ofs.is_open())
            error("can't open output file `%s': %s\n", outfile_name, strerror(errno));
        osp = &ofs;
    } else {
        osp = &std::cout;
    }

    uint32_t file_offset = 0;
    for (int i=0; i<NUM_IMAGES + 1; i++)
    {
        pad_to(*osp, file_offset, i * HEADER_SIZE);
        if (i == 0)
            write_header(*osp, file_offset, header_images[por_image], coldboot);
        else
            write_header(*osp, file_offset, header_images[i - 1], false);
    }
    for (int i=0; i<image_count; i++)
    {
        pad_to(*osp, file_offset, images[i]->offset());
        images[i]->write(*osp, file_offset);
    }

    return EXIT_SUCCESS;
}
