CXX = clang
CC = $(CXX)
DESTDIR ?=
PREFIX ?= /usr/local

ifeq ($(MXE),1)
EXE = .exe
CXX = /usr/local/src/mxe/usr/bin/i686-pc-mingw32-gcc
endif
