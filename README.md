# LINGI2347

### Trivia
* Authors: Gellens Arnaud, Hallet Adrien
* Course: Computer System Security (Pr. Ramin Sadre)
* Academic year 2018-2019 (Q2)

### How to run
This project contains two scripts to fuzz either with mutation or generation. To execute you have to launch the command lines:
* `python3 mutation_fuzzer.py <correct_input> <amount_test_runs> <amount_modifications> <fuzzer_factor> (<output_directory>)`
* `python3 generation_fuzzer <correct_input>`


### Bad inputs
* failing_version.img : fails from versions 20 to 29 (decimal, included) 
