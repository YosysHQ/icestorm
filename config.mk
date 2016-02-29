CXX = clang
CC = $(CXX)
PKG_CONFIG = pkg-config
DESTDIR ?=
PREFIX ?= /usr/local

ifeq ($(MXE),1)
EXE = .exe
CXX = /usr/local/src/mxe/usr/bin/i686-pc-mingw32-gcc
PKG_CONFIG = /usr/local/src/mxe/usr/bin/i686-pc-mingw32-pkg-config
endif
