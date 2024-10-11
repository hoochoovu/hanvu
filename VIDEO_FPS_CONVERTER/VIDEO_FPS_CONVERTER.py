import os
import subprocess

def convert_to_24fps(input_folder, output_folder):
  """
  Converts all video files in the input folder to 24fps and saves them in the output folder.

  Args:
    input_folder: Path to the folder containing the video files.
    output_folder: Path to the folder where the converted videos will be saved.
  """

  for filename in os.listdir(input_folder):
    if filename.endswith(('.mp4', '.mov', '.avi')):  # Add more video extensions if needed
      input_path = os.path.join(input_folder, filename)
      output_path = os.path.join(output_folder, filename)

      # Use FFmpeg to convert the video to 24fps
      command = [
        'ffmpeg',
        '-i', input_path,
        '-r', '24', 
        '-c:v', 'libx264',  # Choose a video codec (libx264 is a good general-purpose option)
        '-c:a', 'copy',  # Copy the audio stream without re-encoding
        output_path
      ]

      try:
        subprocess.run(command, check=True)
        print(f"Converted {filename} to 24fps.")
      except subprocess.CalledProcessError as e:
        print(f"Error converting {filename}: {e}")

# Example usage:
input_folder = "input"
output_folder = "output"

convert_to_24fps(input_folder, output_folder)