" Programs a FPGA by invoking the icestorm commands
"   C + F to: Compile (and sythesize)
"   C + U to: Compile (and sythesize) and Upload to board
map <C-F><C-U> :call FPGACompileAndUpload(1)<CR> 
map <C-F><C-F> :call FPGACompileAndUpload(0)<CR>

" TODO: get module name directly from parsing file
function! FPGACompileAndUpload(upload)
    set ignorecase
    if expand('%:e') == "v"
        write "saves the current file
        let file = expand('%:r') "grabs filename without extension (not needed for now)
        "echo 'Cleaning ' . system("rm -f " . file . ".blif " . file . "*.txt " . file . "*.bin")
        echo "Synthesizing " system("yosys -q -p 'synth_ice40 -top top -blif " . file .".blif' " . file . ".v")
        if a:upload == 1
            echo 'Uploading ' . system("iceprog " . file . ".bin")
        endif
    else
        echo "File not a Verilog file, will not continue."
    endif
endfunction
