PREFIX ?= /usr/local
DEBUG ?= 0
ICEPROG ?= 1
PROGRAM_PREFIX ?=

CXX ?= clang++
CC ?= clang
PKG_CONFIG ?= pkg-config

C_STD ?= c99
CXX_STD ?= c++11
ifeq ($(DEBUG),1)
OPT_LEVEL ?= 0
DBG_LEVEL ?= -ggdb
else
OPT_LEVEL ?= 2
DBG_LEVEL ?=
endif
WARN_LEVEL ?= all

LDLIBS = -lm -lstdc++
CFLAGS += -MD -MP -O$(OPT_LEVEL) $(DBG_LEVEL) -W$(WARN_LEVEL) -std=$(C_STD) -I$(PREFIX)/include
CXXFLAGS += -MD -MP -O$(OPT_LEVEL) $(DBG_LEVEL) -W$(WARN_LEVEL) -std=$(CXX_STD) -I$(PREFIX)/include

DESTDIR ?=
CHIPDB_SUBDIR ?= $(PROGRAM_PREFIX)icebox

ifeq ($(MXE),1)
EXE = .exe
CXX = /usr/local/src/mxe/usr/bin/i686-w64-mingw32.static-gcc
CC = $(CXX)
PKG_CONFIG = /usr/local/src/mxe/usr/bin/i686-w64-mingw32.static-pkg-config
endif

ifeq ($(EMCC),1)
EXE = .js
CC = emcc
CXX = emcc
PREFIX = /
LDFLAGS = -O2 --memory-init-file 0 -s TOTAL_MEMORY=64*1024*1024
SUBDIRS = icebox icepack icemulti icepll icetime icebram
endif

PYTHON3 ?= python3
