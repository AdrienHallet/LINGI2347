import argparse
import random
import subprocess
import os

parser = argparse.ArgumentParser()

parser.add_argument("correct_input", help="a correct input file that works with the converter")
parser.add_argument("test_runs", help="the amount of iterations that generates random input", type=int)
parser.add_argument("max_mods", help="the amount of modifications to make on one file", type=int)
parser.add_argument("factor", help="the mutation factor, from 0 to 1 in percentage", type=float)
parser.add_argument("output_dir", help="the output dir to store mutated files")
parser.add_argument("-v", "--verbose", help="output more things", action="store_true")

# Fuzz the input to achieve crashes and log them
def fuzz(args):
	print('Starting to fuzz')
	fail_counter = 0
	for iteration in range(0, args.test_runs):
		mutated_file_name = args.correct_input
		# Generate mutations
		for sub_iteration in range(0, args.max_mods):
			mutated_file = mutate(read(mutated_file_name), args.factor)
			mutated_file_name = "mutated"+str(iteration)+"_"+ str(sub_iteration) + ".img"
			write(mutated_file, mutated_file_name)
		for sub_iteration in range(0, args.max_mods):
			mutated_file_name = "mutated"+str(iteration)+"_"+ str(sub_iteration) + ".img"
			if test_input(mutated_file_name):
				fail_counter += 1

	if not os.path.exists("failed_inputs"):
		os.mkdir("failed_inputs")
	else:
		os.system("rm failed_inputs/* > /dev/null 2>&1")
	os.system("mv mutated* failed_inputs/")
	print('Generated {} files, {} of which failed the conversion'.format(args.test_runs*args.max_mods, fail_counter))


# Mutate a file with given randomness factor
# Mutation on add/suppress byte(s)
def mutate(file, factor):
	file = bytearray(file)
	mutations = len(file) * factor
	if mutations is 0 and factor is not 0:
		mutations = 1

	while mutations > 0:
		random_byte = random.randint(0,255)
		random_position = random.randint(0, len(file)-1)
		file[random_position] = random_byte
		mutations -= 1

	return file


def test_input(file):
	args = "./converter_static " + file + " test.img"
	try:
		result = subprocess.check_output(args, shell=True, stderr=subprocess.STDOUT) #Run the program
		if("*** The program has crashed" in str(result)):
			print("The converter crashed (file : " + file + ")")
		else:
			os.remove(file)
			return 0
	except subprocess.CalledProcessError:
		print("The converter crashed (file : "+file+")")
	return 1


def read(file):
	with open(file, 'rb') as f:
		buffer = f.read()
	return buffer

def write(content, filename):
	with open(filename, 'wb') as f:
		f.write(content)


if __name__ == '__main__':
	args = parser.parse_args()
	fuzz(args)
