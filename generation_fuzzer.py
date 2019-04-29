import argparse  # used to parse the argument of this program
import binascii
import copy as cp
from subprocess import call
import os
import shutil # used to removed the output folder
import numpy as np # used for the two complement conversion
from random import randint

FIND_ALL = True




def big_to_little_endian(tab, group_by=2):
    # change the endianess
    l = len(tab)
    for a in range(int(l/group_by/2)):
        tmp = tab[group_by*a:group_by*a+group_by]
        tab[group_by*a:group_by*a+group_by] = tab[l-group_by-group_by*a:l-group_by*a]
        tab[l-group_by-group_by*a:l-group_by*a] = tmp
    return tab


def cut_by_piece_of(tab, piece_len):
    return [tab[i*piece_len:(i+1)*piece_len] for i in range(int(len(tab)/piece_len))]

def int_base2(i):
    return int(i, base=2)

def int_to_hex_str(i):
    hex_str = str(hex(i))[2:]
    hex_str_completed = '0' + hex_str if len(hex_str) == 1 else hex_str
    return(hex_str_completed)


def apply(tab, fn):
    return [fn(e) for e in tab]


def tc_int_to_hex_str(i):
    """convert in the two complement system a signed integer into a string representation of the hex value"""
    int_array = tc_int_to_int_array(i)
    return "".join(apply(int_array, int_to_hex_str))


def tc_int_to_int_array(i):
    """"Return an array of four element representing in in the two complement system"""
    binary_two_comp = np.binary_repr(i, width=32)
    pieces = cut_by_piece_of(binary_two_comp, 8)
    pieces_little = big_to_little_endian(pieces, group_by=1)
    val_piece_little = apply(pieces_little, int_base2)

    return val_piece_little

def array_of_random_val(lenght):
    v_min = -(2**31)
    v_max = -v_min - 1
    
    t = [tc_int_to_int_array(randint(v_min, v_max)) for i in range(lenght)]
    return t

# ============================
# ==== ABSTRACT GENERATOR ====
# ============================

class Trans():
    """Generic interface for the transformation supported by the 'apply_transformation' function"""
    def __init__(self, valid_image):
        self.valid_image = valid_image
        self.image = cp.copy(valid_image)


    def generate(self):
        """Retrun a generator of modified image"""
        raise NotImplementedError("Not implemented; this is an abstract class")
    
    def __str__(self):
        """return a description string of the last mutation generated"""
        raise NotImplementedError("Not implemented; this is an abstract class")

    def to_bytes_array(self, s):
        """Convert a string in hexadecimal to an array of bytes"""
        return list(binascii.unhexlify(s))



class Trans_replace(Trans):
    """This partial implementation replace the content of 'vals' at the defined position in the image file"""
    # need to defined:
    # - vals [array of array of byte]
    # - start [int value] (where the value must be inserted)
    # - description [str] (prefix describing the modified part)

    def __init__(self, valid_image):
        super().__init__(valid_image)
        self.stop = self.start + len(self.vals[0])


    def generate(self):

        for v in self.vals:
            self.image[self.start:self.stop] = v
            self.val = v
            yield self.image
    
    def __str__(self):
        str_hex = '['+','.join([hex(i) for i in self.val])+']'
        # str_hex = str([hex(i) for i in self.val])
        # str_hex = str(bytes(self.val))
        return(self.description+"_"+str_hex)



# =============================
# ==== CONCREATE GENERATOR ====
# =============================

class Trans_magic(Trans_replace):
    """Generate modification of the magic number"""
    vals = [
        [0x00,0x0],
        [0x24,0x0],
        [0xff,0xff],
        [ord('a'), ord('b')] # ord is the opposit function of chr
    ]
    start = 0
    description = "magic"



class Trans_version(Trans_replace):
    """Generate modification of the version"""
    vals = [
        [0x00,0x0],
        [0x63,0x0],
        [0x00,0x64],
        [0x64,0x64],
        [0x64,0xff],
        [0xff,0xff],
    ]
    start = 2
    description = "version"


class Trans_version_range(Trans_replace):
    """Generate modification of the version in a range of value from 0 to 105"""
    # make crash for version from [20, 29]
    vals = [tc_int_to_int_array(i)[:2] for i in range(0, 105)]
    start = 2
    description = "version"


class Trans_width(Trans_replace):
    """Generate modification of the width"""
    # the real value is 0x10, 0x00, 0x00, 0x00
    vals = [
        [0x00, 0x00, 0x00, 0x00],
        [0x10, 0x01, 0x00, 0x00],
        [0x10, 0x00, 0x01, 0x00],
        [0x10, 0x00, 0x00, 0x01],
        [0xff, 0xff, 0xff, 0xff],
        [0xf0, 0xff, 0xff, 0xff], # negative value of the real value (in Two's complement system)
    ]
    start = 10
    description = "width"

class Trans_width_rand(Trans_replace):
    """Generate modification of the width randomly"""
    # the real value is 0x10, 0x00, 0x00, 0x00
    vals = array_of_random_val(200)
    start = 10
    description = "width"



class Trans_height(Trans_replace):
    """Generate modification of the height"""
    # the real value is 0x10, 0x00, 0x00, 0x00
    # make crash
    vals = [
        [0x00, 0x00, 0x00, 0x00],
        [0x10, 0x01, 0x00, 0x00],
        [0x10, 0x00, 0x01, 0x00],
        [0x10, 0x00, 0x00, 0x01],
        [0xff, 0xff, 0xff, 0xff], # CRASH
        [0xf0, 0xf0, 0xf0, 0xf0], # CRASH
        [0xf0, 0xff, 0xff, 0xff], # CRASH, negative value of the real value (in Two's complement system)
    ]
    start = 14
    description = "height"


class Trans_height_width(Trans_replace):
    """Generate modification of the lenght of the color table"""
    # the real value is 0x04, 0x00, 0x00, 0x00
    # make crash
    vals = [
        [0x46, 0xEC, 0x00, 0x00, 0x10, 0x58, 0x00, 0x00]
    ]
    # vals = array_of_random_val(200)
    start = 10
    description = "height_rand"


class Trans_height_rand(Trans_replace):
    """Generate modification of the height randomly"""
    # the real value is 0x10, 0x00, 0x00, 0x00
    vals = array_of_random_val(200)
    start = 14
    description = "height"


class Trans_numcolors(Trans_replace):
    """Generate modification of the lenght of the color table"""
    # the real value is 0x04, 0x00, 0x00, 0x00
    # make crash
    vals = [
        [0x00, 0x00, 0x00, 0x00],
        [0x0a, 0x00, 0x00, 0x00],
        [0xff, 0xff, 0xff, 0xff], # CRASH
        [0xf0, 0xf0, 0xf0, 0xf0], # CRASH
        [0xfc, 0xff, 0xff, 0xff], # CRASH, negative value of the real value (in Two's complement system)
    ]
    # vals = array_of_random_val(200)
    start = 18
    description = "numcolors"


class Trans_color_val(Trans_replace):
    """Generate modification of a color value"""
    # the real value is 0x00, 0x00, 0x00, 0x00
    vals = [
        [0x00, 0x00, 0x00, 0x00],
        [0x0a, 0x00, 0x00, 0x00],
        [0xff, 0xff, 0xff, 0xff],
        [0xf0, 0xf0, 0xf0, 0xf0],
        [0xfc, 0xff, 0xff, 0xff],
    ]
    vals = array_of_random_val(200)
    # vals = [tc_int_to_int_array(i) for i in range(0, -10000, -100)]
    # vals = [tc_int_to_int_array(0)]
    start = 22
    description = "color_val"



class Basic(Trans):
    """Generate a valide image with with no trap"""

    def generate(self):
        yield self.to_bytes_array("abcd64006d650002000000020000000200000000000000ffffff0000010100")

    def __str__(self):
        return "basic"



class Empty_author_name(Trans):
    """Generate a valid image with the author field empty"""

    def generate(self):
        yield self.to_bytes_array("abcd64000002000000020000000200000000000000ffffff0000010100")

    def __str__(self):
        return "empty_author"


class Long_author_name(Trans):
    """Generate a valid image with the author name very long 64 bytes"""

    def generate(self):
        yield self.to_bytes_array("abcd6400"+("aa"*64)+"0002000000020000000200000000000000ffffff0000010100")

    def __str__(self):
        return "long_author"


class Long_long_author_name(Trans):
    """Generate a valid image with the author name very long 1024 bytes"""
    # make crash

    def generate(self):
        yield self.to_bytes_array("abcd6400"+("aa"*1024)+"0002000000020000000200000000000000ffffff0000010100")

    def __str__(self):
        return "long_long_author"



class Just_author_name(Trans):
    """Generate the beginning of an image until the author name"""

    def generate(self):
        yield self.to_bytes_array("abcd6400beef")

    def __str__(self):
        return "just_author"



class Just_author_name_w_end(Trans):
    """Generate the beginning of an image until the author name with the 00 at the end"""

    def generate(self):
        yield self.to_bytes_array("abcd6400beef00")

    def __str__(self):
        return "just_author_w_end"



class One_pixels_some_colors(Trans):
    """Generate a valid image with one pixels and some colors defined"""

    def generate(self):
        yield self.to_bytes_array("abcd64006d650001000000010000000200000000000000ffffff0001")

    def __str__(self):
        return "one_pixels_some_colors"



class No_pixels_some_colors(Trans):
    """Generate a valid image with no pixels and some colors defined"""

    def generate(self):
        yield self.to_bytes_array("abcd64006d650000000000000000000200000000000000ffffff00")

    def __str__(self):
        return "no_pixels_some_colors"



class No_pixels_no_colors(Trans):
    """Generate a valid image with no pixels and no colors defined"""

    def generate(self):
        yield self.to_bytes_array("abcd64006d6500000000000000000000000000")

    def __str__(self):
        return "no_pixels_no_colors"



class Out_of_range_color_index(Trans):
    """Generate an image with a pixel color out of range"""

    def generate(self):
        yield self.to_bytes_array("abcd64006d650002000000020000000200000000000000ffffff0000020100")

    def __str__(self):
        return "out_of_range_color_index"



class Many_colors(Trans):
    """Generate a valid image with a long color table"""

    def generate(self):
        nb_colors = [64, 1024]

        for nb_c in nb_colors:
            self.val = nb_c
            nb_c_hex = tc_int_to_hex_str(nb_c)
            yield self.to_bytes_array("abcd64006d65000200000002000000"+nb_c_hex+("ffffff00"*nb_c)+"ffffff0000020100")

    def __str__(self):
        return "many_colors_"+str(self.val)



class Many_pixels(Trans):
    """Generate valid image with a lot of pixels"""

    def generate(self):
        widht_heights = [64, 1024, 20*1000]

        for d in widht_heights:
            self.val = d
            d_hex = tc_int_to_hex_str(d)
            yield self.to_bytes_array("abcd64006d6500"+d_hex+d_hex+"0200000000000000ffffff00"+(d**2 * "01"))

    def __str__(self):
        return "many_pixels_"+str(self.val)+"**2"



# ==================================
# ==== TEST GENERATORS FUNCTION ====
# ==================================

def test_mutation(mutation, description, output_folder):
    global FIND_ALL

    tmp_file_image = "tmp_img_file.img"
    tmp_out_file_image = "tmp_out_img_file.img"
    path = os.path.join(output_folder, tmp_file_image)
    path_out = os.path.join(output_folder, tmp_out_file_image)

    external_lunch_commande = ["./converter_static", path, path_out]
    
    print("\n"+description)
    # print(mutation)
    
    with open(path, 'wb') as f:
        f.write(bytes(mutation))

    return_val  = call(external_lunch_commande)
    # print(return_val)

    if return_val == 0:
        print("ok")
        # os.remove(path)

        return False
    else:
        print("ko")
        dst = os.path.join(output_folder, description)
        os.rename(path, dst)

        # # TODO: remove [start]
        # print("FOUND AT LAST (there is an exit after this line to be sur to see it)")
        # exit()
        # # TODO: remove [stop]

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

        array_hex = list(content)

        return(array_hex)


def parse_args():
    """Parse the input argument of the program"""
    parser = argparse.ArgumentParser(
        description='Take as input a valid image and apply on it small transformation to test the program "converter"')

    parser.add_argument('-i', '--input', required=True, metavar='I', nargs=1,
                        help='input  valid image file')
    parser.add_argument('-o', '--output', metavar='O', nargs=1,
                        help='output folder')
    args = parser.parse_args()
    return args


def main():
    transformations = [
        Trans_magic,
        Trans_version,
        Trans_version_range, # crash
        Trans_width,
        Trans_width_rand,
        Trans_height, # make crash
        Trans_height_rand, # (make crash)
        Trans_numcolors, # make crash
        Trans_color_val,
        Basic,
        Empty_author_name,
        Long_author_name,
        Long_long_author_name, # make crash !!
        Just_author_name,
        Just_author_name_w_end,
        One_pixels_some_colors,
        No_pixels_some_colors,
        No_pixels_no_colors,
        Out_of_range_color_index,
        Many_colors,
        Many_pixels,
        # Trans_height_width
    ]

    args = parse_args()
    img_file_name = args.input[0]
    output_folder = args.output[0]

    make_output_directory(output_folder)
    valid_image = decode(img_file_name)

    apply_transformation(valid_image, transformations, output_folder)




if __name__ == '__main__':
    main()
