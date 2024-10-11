import os
import numpy as np
from PIL import Image
from PIL import ImageOps

# Check if the Pillow-SIMD package is installed
try:
    from pillow_simd import PImage
except ImportError:
    print("Pillow-SIMD package not found. Using CPU-based Pillow instead.")
    from PIL import Image

# Define the input and output folders
input_folder = 'fg'
output_folder = 'output_trim'

# Check if the input and output folders exist, create them if not
if not os.path.exists(input_folder):
    os.makedirs(input_folder)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Loop through all images in the input folder
for filename in os.listdir(input_folder):
    # Check if the file is an image
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):

        # Open the image
        image_path = os.path.join(input_folder, filename)
        image = Image.open(image_path)

        # Get the image size
        width, height = image.size

        # Crop the left and right sides of the image by 29 pixels
        cropped_image = image.crop((37, 0, width - 37, height))

        # Save the cropped image in the output folder
        output_path = os.path.join(output_folder, filename)
        cropped_image.save(output_path)

        print(f'Image {filename} has been cropped and saved to {output_path}')