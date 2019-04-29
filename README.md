# LINGI2347

### Trivia
* Authors: Gellens Arnaud, Hallet Adrien
* Course: Computer System Security (Pr. Ramin Sadre)
* Academic year 2018-2019 (Q2)

### How to run
This project contains two scripts to fuzz either with mutation or generation. To execute you have to launch the command lines:
* `python3 mutation_fuzzer.py <correct_input> <amount_test_runs> <amount_modifications> <fuzzer_factor> (<output_directory>)`
* `python3 generation_fuzzer -i <correct_input> -o <output_directory>`

Both fuzzers will generate failing input files and save them in the directory. The mutation fuzzer generates files with the name model mutatedX_Y.img where X is the general iteration number and Y is the amount of mutation done on iteration X. The generation fuzzer names the files accordingly to the applied modification.


### Bad inputs
* failing_version.img : fails from versions 20 to 29 (decimal, included) 
* failing_colornumber.img : some (todo: determine the range ?) values for the color number crash the program. Negative values seem to be the key to obtain a crash
* failing_heightandwidth.img : fails on combinations of width and height. A certain height may be accepted, but not with all accepted width.
* failing_authorname.img : fails when the authorname is too long (here 1024 bytes)
* failing_height.img : fails when the height is negative
