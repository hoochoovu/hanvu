import os
import shutil

def parse_commentary(file_path, output_folder, processed_folder):
  """Parses a .txt file into three separate files based on the [Text] sections.

  Args:
      file_path: The path to the .txt file to be parsed.
      output_folder: The path to the folder where the parsed files will be saved.
      processed_folder: The path to the folder where the processed .txt files will be moved.
  """

  try:
    with open(file_path, 'r', encoding='utf-8') as file:
      content = file.read()
      print(f"Content of {file_path}:")
      print(content)  # Print the content for debugging

    sections = content.split('[')

    for section in sections[1:]:
      parts = section.split(']')
      section_name = parts[0].strip()
      section_content = parts[1].strip()

      output_file_path = os.path.join(output_folder, f"{section_name}.txt")
      with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(section_content)

    # Move the processed file to the processed folder
    shutil.move(file_path, processed_folder)

  except Exception as e:
    print(f"Error processing {file_path}: {e}")

def main():
  """Reads .txt files from a folder and parses them."""

  # Get folder paths 
  input_folder = r"E:\Python_Practice\AutoSeparate_Gemini\Input"
  output_folder = r"E:\Python_Practice\AutoSeparate_Gemini\Output"
  processed_folder = r"E:\Python_Practice\AutoSeparate_Gemini\Processed"

  # Create output and processed folders if they don't exist
  os.makedirs(output_folder, exist_ok=True)
  os.makedirs(processed_folder, exist_ok=True)

  # Process files in the input folder
  for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
      file_path = os.path.join(input_folder, filename)
      parse_commentary(file_path, output_folder, processed_folder)

if __name__ == "__main__":
  main()