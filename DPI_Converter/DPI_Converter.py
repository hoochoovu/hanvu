import os
import subprocess
import concurrent.futures
from PIL import Image
from functools import partial

# Set your input and output folders here
INPUT_FOLDER = r"E:\Python_Practice\DPI_Converter\input"
OUTPUT_FOLDER = r"E:\Python_Practice\DPI_Converter\output"

# Set your desired output format here ('jpg' or 'png')
OUTPUT_FORMAT = 'jpg'

# Number of worker threads for parallel processing
NUM_WORKERS = 8

def resize_with_ffmpeg(input_path, output_path, new_width, new_height):
    try:
        # Command to resize image using FFmpeg software scaling and GPU encoding
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', f'scale={new_width}:{new_height}',   # Software scaling
            '-c:v', 'h264_nvenc',                      # GPU encoding (H.264)
            '-pix_fmt', 'yuvj420p',                    # Ensure JPEG compatibility
            output_path
        ]
        # Execute FFmpeg command
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error processing {input_path}: {e}")

# Function to process image with FFmpeg
def process_image_with_ffmpeg(input_path, output_path, target_dpi=300):
    try:
        # Open the image to get its dimensions
        pil_img = Image.open(input_path)
        original_width, original_height = pil_img.size
        
        # Assume original DPI is 72 if not specified
        original_dpi = 72

        # Calculate new dimensions based on target DPI
        scale_factor = target_dpi / original_dpi
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Call FFmpeg to resize using software scaling and GPU encoding
        resize_with_ffmpeg(input_path, output_path, new_width, new_height)

    except Exception as e:
        print(f"Error processing {input_path}: {e}")

# Wrapper to handle arguments in parallel processing
def process_image_wrapper(args):
    try:
        process_image_with_ffmpeg(*args)
        return f"Processed: {args[0]} -> {args[1]}"
    except Exception as e:
        return f"Error processing {args[0]}: {str(e)}"

# Function to iterate over input directories and apply processing
def process_directory(input_dir, output_dir, output_format):
    tasks = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_path)
                output_path = os.path.splitext(output_path)[0] + f'.{output_format.lower()}'
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                tasks.append((input_path, output_path))
    
    # Parallel processing of images
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        results = list(executor.map(process_image_wrapper, tasks))
    
    # Display results
    for result in results:
        print(result)

# Main function
def main():
    process_directory(INPUT_FOLDER, OUTPUT_FOLDER, OUTPUT_FORMAT)
    print(f"Image processing complete. Results saved in {OUTPUT_FOLDER}")

if __name__ == "__main__":
    main()
