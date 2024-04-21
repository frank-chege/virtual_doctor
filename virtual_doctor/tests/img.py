
from rembg import *
from PIL import Image
input_path = '/home/frank/Downloads/test1.jpeg'
output_path = '/home/frank/Downloads/res1.jpeg'
input = Image.open(input_path)
output = remove(input)
output.save(output_path)