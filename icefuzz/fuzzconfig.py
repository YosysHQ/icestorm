import os

num = 20

device_class = os.getenv("ICEDEVICE")

if device_class == "8k":
    num_ramb40 = 32
    num_iobanks = 4
    num_dsp = 0

    pins="""
        A1  A2          A5  A6  A7      A9  A10 A11             A15 A16
        B1  B2  B3  B4  B5  B6  B7  B8  B9  B10 B11 B12 B13 B14 B15 B16
        C1  C2  C3  C4  C5  C6  C7  C8  C9  C10 C11 C12 C13 C14     C16
        D1  D2  D3  D4  D5  D6  D7  D8  D9  D10 D11     D13 D14 D15 D16
        E2  E3  E4  E5  E6          E9  E10 E11     E13 E14     E16
        F1  F2  F3  F4  F5      F7      F9      F11 F12 F13 F14 F15 F16
        G1  G2  G3  G4  G5                  G10 G11 G12 G13 G14 G15 G16
        H1  H2  H3  H4  H5  H6                  H11 H12 H13 H14     H16
        J1  J2  J3  J4  J5                  J10 J11 J12 J13 J14 J15 J16
        K1      K3  K4  K5              K9      K11 K12 K13 K14 K15 K16
        L1      L3  L4  L5  L6  L7      L9  L10 L11 L12 L13 L14     L16
        M1  M2  M3  M4  M5  M6  M7  M8  M9      M11 M12 M13 M14 M15 M16
        N2  N3  N4  N5  N6  N7      N9  N10     N12             N16
        P1  P2      P4  P5  P6  P7  P8  P9  P10 P11 P12 P13 P14 P15 P16
        R1  R2  R3  R4  R5  R6          R9  R10 R11 R12     R14 R15 R16
        T1  T2  T3      T5  T6  T7  T8  T9  T10 T11     T13 T14 T15 T16
    """.split()

    gpins = "C8 F7 G1 H11 H16 I3 K9 R9".split()

elif device_class == "384":
    num_ramb40 = 0
    num_iobanks = 3
    num_dsp = 0

    pins = """
        A1 A2 A3 A4 A5 A6 A7
        B1 B2 B3 B4
        C1 C2    C4 C5 C6 C7
        D1 D2 D3 D4    D6 D7
           E2          E6 E7
        F1 F2 F3 F4 F5 F6 F7
        G1    G3 G4    G6
    """.split()

    gpins = "B4 C4 D2 D6 D7 E2 F3 F4".split()

elif device_class == "1k":
    num_ramb40 = 16
    num_iobanks = 4
    num_dsp = 0

    pins = """
        1 2 3 4 7 8 9 10 11 12 19 22 23 24 25 26 28 29 31 32 33 34
        37 38 41 42 43 44 45 47 48 52 56 58 60 61 62 63 64
        73 74 75 76 78 79 80 81 87 88 90 91 95 96 97 98 101 102 104 105 106 107
        112 113 114 115 116 117 118 119 120 121 122 134 135 136 137 138 139 141 142 143 144
    """.split()

    gpins = "20 21 49 50 93 94 128 129".split()

elif device_class == "4k":
    num_ramb40 = 20
    num_iobanks = 2
    num_dsp = 0

    # TODO(awygle) add F5 G6 F6 E6 which are constrained to (config) SPI.
    pins = """
        A1 A2 A3 A4 A5 A6 A7
        B1 B2    B4    B6 B7
        C1    C3 C4    C6 C7
        D1 D2 D3       D6 D7
        E1 E2 E3 E4 E5    E7
           F2 F3 F4       F7
              G3
    """.split()

    gpins = "A3 A4 D2 E2 E5 G3".split()

elif device_class == "5k":
    num_ramb40 = 30
    num_iobanks = 2
    num_dsp = 8
    num_spram256ka = 4
    #TODO(tannewt): Add 39, 40, 41 to this list. It causes placement failures for some reason.
    # Also add 14 15 16 17 which are constrained to SPI.
    #TODO(daveshah1): Add back I3C IO 23 which cause placement failures when assigned to
    #an SB_IO clk_in
    pins = """2 3 4 6 9 10 11 12
    13 18 19 20 21
    25 26 27 28 31 32 34 35 36
    37 38 42 43 44 45 46 47 48
    """.split()

    #TODO(tannewt): Add 39, 40, 41 to this list. It causes placement failures for some reason.
    gpins = "20 35 37 44".split()
    led_pins = "39 40 41".split()

elif device_class == "u4k":
    num_ramb40 = 20
    num_iobanks = 2
    num_dsp = 4

    #TODO(tannewt): Add 39, 40, 41 to this list. It causes placement failures for some reason.
    # Also add 14 15 16 17 which are constrained to SPI.
    #TODO(daveshah1): Add back I3C IO 23 which cause placement failures when assigned to
    #an SB_IO clk_in
    pins = """2 3 4 6 9 10 11 12
    13 18 19 20 21
    25 26 27 28 31 32 34 35 36
    37 38 42 43 44 45 46 47 48
    """.split()

    #TODO(tannewt): Add 39, 40, 41 to this list. It causes placement failures for some reason.
    gpins = "20 35 37 44".split()
    led_pins = "39 40 41".split()

def output_makefile(working_dir, fuzzname):
  with open(working_dir + "/Makefile", "w") as f:
      print("all: %s" % " ".join(["%s_%02d.bin" % (fuzzname, i) for i in range(num)]), file=f)
      for i in range(num):
          basename = "%s_%02d" % (fuzzname, i)
          print("%s.bin:" % basename, file=f)
          print("\t-bash ../icecube.sh %s > %s.log 2>&1 && rm -rf %s.tmp || tail %s.log" % (basename, basename, basename, basename), file=f)
          print("\tpython3 ../glbcheck.py %s.asc %s.glb" % (basename, basename), file=f)
