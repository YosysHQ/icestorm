icebox_chipdb = find_program('icebox_chipdb.py')

chipdb_384 = custom_target('chipdb-384',
  output : 'chipdb-384.txt',
  command : [icebox_chipdb, '-3'],
  capture : true,
  install : true,
  install_dir : 'share/icebox/')

chipdb_1k = custom_target('chipdb-1k',
  output : 'chipdb-1k.txt',
  command : [icebox_chipdb],
  capture : true,
  install : true,
  install_dir : 'share/icebox/')

chipdb_8k = custom_target('chipdb-8k',
  output : 'chipdb-8k.txt',
  command : [icebox_chipdb, '8'],
  capture : true,
  install : true,
  install_dir : 'share/icebox')


python_sources = [
	'icebox.py',
	'iceboxdb.py',
	'icebox_chipdb.py',
	'icebox_diff.py',
	'icebox_explain.py',
	'icebox_colbuf.py',
	'icebox_html.py',
	'icebox_maps.py',
	'icebox_vlog.py',
	'icebox_stat.py']

install_data(python_sources, install_dir:'bin', install_mode:'rwxr-xr-x')

