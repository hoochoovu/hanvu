import os
import shutil

def copy_sizexsize_contents(input_folder, output_folder):
  """
  Copies the contents of "sizexsize" subfolders from the input folder to the output folder.

  Args:
    input_folder: The path to the folder containing subfolders.
    output_folder: The path to the folder where the "sizexsize" contents will be copied.
  """

  for root, dirs, files in os.walk(input_folder):
    for dir_name in dirs:
      if dir_name == "1x1":
        source_path = os.path.join(root, dir_name)
        # Copy the contents of the "sizexsize" folder to the output folder
        for item in os.listdir(source_path):
          item_path = os.path.join(source_path, item)
          destination_path = os.path.join(output_folder, item)
          if os.path.isdir(item_path):
            shutil.copytree(item_path, destination_path)  # Copy subfolders recursively
          else:
            shutil.copy2(item_path, destination_path)      # Copy files

if __name__ == "__main__":
  input_folder = r"E:\Python_Practice\Printify Mockup Image Combiner\Canva Mockup Generator\output"
  output_folder = "output"

  # Create the output folder if it doesn't exist
  os.makedirs(output_folder, exist_ok=True)

  copy_sizexsize_contents(input_folder, output_folder)
  print("Contents of subfolders copied successfully!")