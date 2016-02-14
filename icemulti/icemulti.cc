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

#include <stdio.h>
#include <stdlib.h>

#define log(...) fprintf(stderr, __VA_ARGS__);
#define info(...) do { if (log_level > 0) fprintf(stderr, __VA_ARGS__); } while (0)
#define error(...) do { fprintf(stderr, "Error: " __VA_ARGS__); exit(1); } while (0)

int log_level = 0;

static const int NUM_IMAGES = 4;
static const int NUM_HEADERS = NUM_IMAGES + 1;
static const int HEADER_SIZE = 32;

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
                       std::istream &ifs)
{
    const size_t bufsize = 8192;
    uint8_t *buffer = new uint8_t[bufsize];

    while(!ifs.eof()) {
        ifs.read(reinterpret_cast<char *>(buffer), bufsize);
        if (ifs.bad())
            error("Read error on input image");
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
    Image(const char *filename) : ifs(filename, std::ifstream::binary) {}

    size_t size();
    void write(std::ostream &ofs, uint32_t &file_offset);
    void place(uint32_t o) { offs = o; }
    uint32_t offset() const { return offs; }
};

size_t Image::size()
{
    ifs.seekg (0, ifs.end);
    size_t length = ifs.tellg();
    ifs.seekg (0, ifs.beg);
    return length;
}

void Image::write(std::ostream &ofs, uint32_t &file_offset)
{
    write_file(ofs, file_offset, ifs);
}

class Header {
    uint32_t image_offs;
    bool coldboot_flag;
    bool empty;
public:
    Header() : empty(true) {}
    Header(const Image &i) :
        image_offs(i.offset()), coldboot_flag(false), empty(false) {}
    void set_coldboot_flag() { coldboot_flag = true; }
    void write(std::ostream &ofs, uint32_t &file_offset);
};

void Header::write(std::ostream &ofs, uint32_t &file_offset)
{
    if (empty)
        return;

    // Preamble
    write_byte(ofs, file_offset, 0x7e);
    write_byte(ofs, file_offset, 0xaa);
    write_byte(ofs, file_offset, 0x99);
    write_byte(ofs, file_offset, 0x7e);

    // Boot mode
    write_byte(ofs, file_offset, 0x92);
    write_byte(ofs, file_offset, 0x00);
    write_byte(ofs, file_offset, (coldboot_flag? 0x10: 0x00));

    // Boot address
    write_byte(ofs, file_offset, 0x44);
    write_byte(ofs, file_offset, 0x03);
    write_byte(ofs, file_offset, (image_offs >> 16) & 0xff);
    write_byte(ofs, file_offset, (image_offs >> 8) & 0xff);
    write_byte(ofs, file_offset, image_offs & 0xff);

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

void usage()
{
    log("\n");
    log("Usage: icemulti [options] input-files\n");
    log("\n");
    log(" -c\n");
    log(" coldboot mode, power on reset image is selected by CBSEL0/CBSEL1\n");
    log("\n");
    log(" -p0, -p1, -p2, -p3\n");
    log(" select power on reset image when not using coldboot mode\n");
    log("\n");
    log(" -o filename\n");
    log(" write output image to file instead of stdout\n");
    log("\n");
    log(" -v\n");
    log(" verbose (repeat to increase verbosity)\n");
    log("\n");
    exit(1);
}

int main(int argc, char **argv)
{
    bool coldboot = false;
    int por_image = 0;
    int image_count = 0;
    Header headers[NUM_HEADERS];
    std::unique_ptr<Image> images[NUM_IMAGES];
    const char *outfile_name = NULL;

    for (int i = 1; i < argc; i++)
    {
	if (argv[i][0] == '-' && argv[i][1]) {
            for (int j = 1; argv[i][j]; j++)
                if (argv[i][j] == 'c') {
                    coldboot = true;
                } else if (argv[i][j] == 'p' && argv[i][j+1]) {
                    por_image = argv[i][++j] - '0';
                } else if (argv[i][j] == 'o') {
                    if (argv[i][j+1])
                        outfile_name = &argv[i][j+1];
                    else if(i+1 < argc)
                        outfile_name = argv[++i];
                    else
                        usage();
                    break;
                } else if (argv[i][j] == 'v') {
                    log_level++;
                } else
                    usage();
            continue;
        }

        if (image_count >= NUM_IMAGES)
            error("Too many images supplied\n");
        images[image_count++].reset(new Image(argv[i]));
    }

    if (!image_count)
        usage();

    if (coldboot && por_image != 0)
        error("Can't select power on reset boot image in cold boot mode\n");

    if (por_image >= image_count)
        error("Specified non-existing image for power on reset\n");

    // Place images
    uint32_t offs = 0x100;
    for (int i=0; i<image_count; i++) {
        images[i]->place(offs);
        offs += images[i]->size();

        // Align to 4K
        if (offs & 0xfff) {
            offs |= 0xfff;
            offs++;
        }
    }

    // Populate headers
    for (int i=0; i<image_count; i++)
        headers[i + 1] = Header(*images[i]);
    headers[0] = headers[por_image + 1];
    for (int i=image_count; i < NUM_IMAGES; i++)
        headers[i + 1] = headers[0];
    if (coldboot)
        headers[0].set_coldboot_flag();

    std::ofstream ofs;
    std::ostream *osp;

    if (outfile_name != NULL) {
        ofs.open(outfile_name, std::ofstream::binary);
        if (!ofs.is_open())
            error("Failed to open output file.\n");
        osp = &ofs;
    } else {
        osp = &std::cout;
    }

    uint32_t file_offset = 0;
    for (int i=0; i<NUM_HEADERS; i++)
    {
        pad_to(*osp, file_offset, i * HEADER_SIZE);
        headers[i].write(*osp, file_offset);
    }
    for (int i=0; i<image_count; i++)
    {
        pad_to(*osp, file_offset, images[i]->offset());
        images[i]->write(*osp, file_offset);
    }

    info("Done.\n");
    return 0;
}
