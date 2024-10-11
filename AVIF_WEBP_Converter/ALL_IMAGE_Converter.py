import os
import subprocess

def convert_image_ffmpeg(input_path, output_path, output_format):
    try:
        # Determine the correct output file name with format
        output_file = os.path.splitext(output_path)[0] + "." + output_format.lower()

        # Use FFmpeg to convert the image
        ffmpeg_command = [
            "ffmpeg", "-i", input_path, 
            output_file
        ]

        # Run the FFmpeg command
        subprocess.run(ffmpeg_command, check=True)
        print(f"Converted: {input_path} -> {output_file}")
    
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {input_path}: {e}")

def process_folder(input_folder, output_folder, output_format):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            input_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, input_folder)
            output_dir = os.path.join(output_folder, relative_path)
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            output_path = os.path.join(output_dir, file)
            convert_image_ffmpeg(input_path, output_path, output_format)

if __name__ == "__main__":
    input_folder = "input"
    output_folder = "output"
    output_format = "jpg"  # "png" or "jpg"
    
    process_folder(input_folder, output_folder, output_format)
