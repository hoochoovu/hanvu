import os
import re
import docx

def natural_sort(list_of_strings):
  """Sorts a list of strings in a natural order, handling numeric parts correctly.

  Args:
      list_of_strings: The list of strings to be sorted.

  Returns:
      A new list containing the sorted strings.
  """
  convert = lambda text: int(text) if text.isdigit() else text
  alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
  return sorted(list_of_strings, key=alphanum_key)

def append_files_to_word(folder_path):
  """Appends all text files in a folder (including subfolders) to a Word document.

  Args:
      folder_path: The path to the folder containing the text files.
  """
  doc = docx.Document()

  # Get all text files recursively
  for root, _, files in os.walk(folder_path):
    for file in natural_sort(files):
      if file.endswith(".txt"):
        file_path = os.path.join(root, file)
        with open(file_path, "r", encoding="utf-8") as f:
          content = f.read()
          doc.add_paragraph(content)

  # Save the Word document
  doc.save("combined_files.docx")

if __name__ == "__main__":
  # Set the input folder path here
  folder_path = r"E:\ChatBot Therapy\Marcus Aurelius\Modern Stoic Book\The Main Book Sub Conscious Stoic\1"  
  append_files_to_word(folder_path)
  print("Files appended to 'combined_files.docx'")