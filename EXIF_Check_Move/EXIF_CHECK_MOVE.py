import os
import shutil

def contains_samurai_in_file(image_path):
    """Checks if the word 'samurai' appears anywhere in the file's content."""
    try:
        # Open the image file in binary mode
        with open(image_path, 'rb') as f:
            data = f.read()
            # Check if 'samurai' is present in the binary data
            if b'samurai' in data.lower():
                return True
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
    return False

def move_image(image_path, destination_folder):
    """Moves an image to the destination folder."""
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    shutil.move(image_path, destination_folder)

def process_images(folder, destination_folder):
    """Processes all images in the folder, checking for 'samurai' in file data."""
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif')):
                image_path = os.path.join(root, file)
                if contains_samurai_in_file(image_path):
                    print(f"Moving {file} to {destination_folder}")
                    move_image(image_path, destination_folder)

if __name__ == '__main__':
    # Define your folder paths here
    input_folder = r'E:\Davinci\STOIC Background Videos\V3\Images\Vertical V2'
    output_folder = r'E:\Davinci\STOIC Background Videos\V3\Images\Samurai'
    
    process_images(input_folder, output_folder)
