import argparse  # used to parse the argument of this program
import binascii
import copy as cp
from subprocess import call
import os
import shutil # used to removed the output folder

FIND_ALL = False


class Trans():
    def __init__(self, valid_image):
        self.valid_image = valid_image
        self.image = cp.copy(valid_image)


    def generate(self):
        self.i = 42
        yield 42
        # for i in range(3):
        #     self.i = i
        #     yield(i)
    
    def __str__(self):
        """return a description string of the last mutation generated"""
        return(str(self.i))



class Trans_magic(Trans):

    def generate(self):
        vals = [
            [0x00,0x0],
            [0x24,0x0],
            [0xff,0xff],
        ]
        for v in vals:
            self.image[0:2] = v
            self.magic = v
            yield self.image

    def __str__(self):
        str_hex = '['+','.join([hex(i) for i in self.magic])+']'
        # str_hex = str([hex(i) for i in self.magic])
        # str_hex = str(bytes(self.magic))
        return("magic_"+str_hex)




def test_mutation(mutation, description, output_folder):
    global FIND_ALL

    fake_fail_commande = "ls test"
    fake_valid_commande = "ls"

    # TODO change the lunch commande
    external_lunch_commande = fake_fail_commande
    external_lunch_commande = fake_valid_commande
    
    print("\n"+description)
    print(mutation)

    tmp_file_image = "tmp_img_file.img"
    path = os.path.join(output_folder, tmp_file_image)
    
    with open(path, 'wb') as f:
        f.write(bytes(mutation))

    return_val  = call(external_lunch_commande)
    print(return_val)

    if return_val == 0:
        print("ok")
        os.remove(path)

        return False
    else:
        print("ko")
        dst = os.path.join(output_folder, description)
        os.rename(path, dst)

        return not FIND_ALL # in case we want failed image, the return value muste be False


def apply_transformation(valid_image, trans_types, output_folder):
    for transformation in trans_types:
        t = transformation(valid_image)

        for mutation in t.generate():
            stop = test_mutation(mutation, str(t), output_folder)
            
            if stop:
                break


def make_output_directory(output_folder):  
    if os.path.exists(output_folder):  # clear the directory
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)



def decode(img_file_name):

    with open(img_file_name, 'rb') as f:
        content = f.read()


        print("original:")
        print(content)
        # byte_str_hex = binascii.hexlify(content) # allow to have a visual way to see the content
        # str_hex = byte_str_hex.decode("utf-8")
        # print(str_hex)

        print("\noriginal in hex:")
        print(content)
        array_hex = list(content)

        return(array_hex)

        # array_hex[0:2] = [0x00,0x00]
        # print("\nTransformed:")
        # print(array_hex)
        # print("\back to original format 2:")
        # array_hex_2 = bytes(array_hex)
        # print(array_hex_2)
        # exit()


def parse_args():
    """Parse the input argument of the program"""
    parser = argparse.ArgumentParser(
        description='Take as input a valide image and apply on it small transformation to test the program "converter"')

    parser.add_argument('-i', '--input', required=True, metavar='I', nargs=1,
                        help='input  valide image file')
    parser.add_argument('-o', '--output', metavar='O', nargs=1,
                        help='output folder')
    args = parser.parse_args()
    return args


def main():
    transformations = [
        Trans_magic
    ]

    args = parse_args()
    img_file_name = args.input[0]
    output_folder = args.output[0]

    make_output_directory(output_folder)
    valid_image = decode(img_file_name)

    apply_transformation(valid_image, transformations, output_folder)




if __name__ == '__main__':
    main()
