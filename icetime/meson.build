timings_gen = find_program('timings.py')

timings = custom_target('timings',
  input : ['../icefuzz/timings_hx1k.txt', '../icefuzz/timings_hx8k.txt',
           '../icefuzz/timings_lp1k.txt', '../icefuzz/timings_lp8k.txt',
           '../icefuzz/timings_lp384.txt'],
  output : 'timings.inc',
  command : [timings_gen],
  capture : true)

PREFIX = get_option('prefix')

cpp_args = ['-DPREFIX="@0@"'.format(PREFIX), '-DCHIPDB_SUBDIR="@0@"'.format(CHIPDB_SUBDIR)]

icetime = executable('icetime', 'icetime.cc',timings ,
 cpp_args:cpp_args,
 install:true)

