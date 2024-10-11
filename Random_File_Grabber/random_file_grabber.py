import os
import random
import shutil

def copy_random_file_from_subfolders(input_folder, output_folder):
  """
  Copies one random file from each subfolder in the input folder to the output folder.

  Args:
      input_folder: The path to the input folder.
      output_folder: The path to the output folder.
  """

  for subfolder_name in os.listdir(input_folder):
    subfolder_path = os.path.join(input_folder, subfolder_name)

    # Check if it's a directory
    if os.path.isdir(subfolder_path):
      files = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]

      if files:
        # Choose a random file
        random_file = random.choice(files)
        source_path = os.path.join(subfolder_path, random_file)
        destination_path = os.path.join(output_folder, random_file)

        # Copy the file
        shutil.copy2(source_path, destination_path)
        print(f"Copied '{random_file}' from '{subfolder_name}' to '{output_folder}'")
      else:
        print(f"No files found in '{subfolder_name}'")

if __name__ == "__main__":
  input_folder = r"E:\ETSY ETSY ETSY\Design for Trends\Scary Halloween Faces\Mockup\Poster Far Mockup"  # Replace with your input folder path
  output_folder = "output" # Replace with your output folder path

  # Create the output folder if it doesn't exist
  os.makedirs(output_folder, exist_ok=True)

  copy_random_file_from_subfolders(input_folder, output_folder) 