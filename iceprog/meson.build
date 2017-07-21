libftdi1 = dependency('libftdi1', required:true)

iceprog = executable('iceprog', 'iceprog.c',dependencies:libftdi1 , install:true)

install_man('iceprog.1')
