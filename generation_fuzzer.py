import argparse  # used to parse the argument of this program
import binascii
import copy as cp
from subprocess import call
import os
import shutil # used to removed the output folder

FIND_ALL = False


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
        """Convert a string in exadecimal to an array of bytes"""
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
    start = 8
    description = "width"



class Trans_height(Trans_replace):
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
    start = 12
    description = "height"



class Trans_numcolors(Trans_replace):
    """Generate modification of the width"""
    # the real value is 0x04, 0x00, 0x00, 0x00
    vals = [
        [0x00, 0x00, 0x00, 0x00],
        [0x0a, 0x00, 0x00, 0x00],
        [0xff, 0xff, 0xff, 0xff],
        [0xfc, 0xff, 0xff, 0xff], # negative value of the real value (in Two's complement system)
    ]
    start = 16
    description = "numcolors"



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
    print(mutation)
    
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

        # TODO: remove [start]
        print("FOUND AT LAST (there is an exit after this line to be sur to see it)")
        exit()
        # TODO: remove [stop]

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
        description='Take as input a valide image and apply on it small transformation to test the program "converter"')

    parser.add_argument('-i', '--input', required=True, metavar='I', nargs=1,
                        help='input  valide image file')
    parser.add_argument('-o', '--output', metavar='O', nargs=1,
                        help='output folder')
    args = parser.parse_args()
    return args


def main():
    transformations = [
        Trans_magic,
        Trans_version,
        Trans_width,
        Trans_height,
        Trans_numcolors,
        Basic,
        Empty_author_name,
        No_pixels_some_colors,
        No_pixels_no_colors,
        Out_of_range_color_index,
    ]

    args = parse_args()
    img_file_name = args.input[0]
    output_folder = args.output[0]

    make_output_directory(output_folder)
    valid_image = decode(img_file_name)

    apply_transformation(valid_image, transformations, output_folder)




if __name__ == '__main__':
    main()
