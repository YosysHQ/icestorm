#!/bin/bash

pbm_to_ppm() {
	read line; echo "P3"
	read line; echo "$line"; echo "2"
	sed "s,0,x,g; s,1,y,g; s,x,$1,g; s,y,$2,g;"

}

../icepack/icepack -uc  -B0 ../tests/example.bin | pbm_to_ppm "0 0 0" "0 0 2" > checkerboard_0.ppm
../icepack/icepack -ucc -B0 ../tests/example.bin | pbm_to_ppm "0 0 0" "0 1 0" > checkerboard_1.ppm
../icepack/icepack -uc  -B1 ../tests/example.bin | pbm_to_ppm "0 0 0" "0 1 1" > checkerboard_2.ppm
../icepack/icepack -ucc -B1 ../tests/example.bin | pbm_to_ppm "0 0 0" "1 0 0" > checkerboard_3.ppm
../icepack/icepack -uc  -B2 ../tests/example.bin | pbm_to_ppm "0 0 0" "1 0 1" > checkerboard_4.ppm
../icepack/icepack -ucc -B2 ../tests/example.bin | pbm_to_ppm "0 0 0" "1 1 0" > checkerboard_5.ppm
../icepack/icepack -uc  -B3 ../tests/example.bin | pbm_to_ppm "0 0 0" "1 1 1" > checkerboard_6.ppm
../icepack/icepack -ucc -B3 ../tests/example.bin | pbm_to_ppm "0 0 0" "0 1 0" > checkerboard_7.ppm

convert -evaluate-sequence add checkerboard_[01234567].ppm checkerboard.png
rm -f checkerboard_[01234567].ppm

