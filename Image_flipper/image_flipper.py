import os
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS

def flip_images(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get the list of image files in the input folder
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'))]

    for i, image_file in enumerate(image_files):
        image_path = os.path.join(input_folder, image_file)
        with Image.open(image_path) as img:
            # Try to retain the EXIF data
            exif_data = img.info.get('exif')

            # Flip every other image horizontally
            if i % 2 == 1:
                img = ImageOps.mirror(img)  # Flip horizontally while preserving metadata

            # Save the image with EXIF data (if available)
            output_path = os.path.join(output_folder, image_file)
            if exif_data:
                img.save(output_path, exif=exif_data)
            else:
                img.save(output_path)

    print(f"Processed {len(image_files)} images. Every other image was flipped, and metadata was preserved.")


if __name__ == '__main__':
    input_folder = r'E:\Dataset\All Photo Creations for Video Generation\Artwork\Leonid Afremov Style\Vertical'  # Replace with your input folder path
    output_folder = r'output'  # Replace with your output folder path
    flip_images(input_folder, output_folder)
