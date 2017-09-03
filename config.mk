PREFIX ?= /usr/local

CXX ?= clang++
CC ?= clang
PKG_CONFIG ?= pkg-config

C_STD ?= c99
CXX_STD ?= c++11
OPT_LEVEL ?= 0
WARN_LEVEL ?= all

LDLIBS = -lm -lstdc++
CFLAGS += -MD -O$(OPT_LEVEL) -ggdb -W$(WARN_LEVEL) -std=$(C_STD) -I$(PREFIX)/include
CXXFLAGS += -MD -O$(OPT_LEVEL) -ggdb -W$(WARN_LEVEL) -std=$(CXX_STD) -I$(PREFIX)/include

DESTDIR ?=
CHIPDB_SUBDIR ?= icebox

ifeq ($(MXE),1)
EXE = .exe
CXX = /usr/local/src/mxe/usr/bin/i686-w64-mingw32.static-gcc
CC = $(CXX)
PKG_CONFIG = /usr/local/src/mxe/usr/bin/i686-w64-mingw32.static-pkg-config
endif
