import os
import docx2txt
from ebooklib import epub
from ebooklib.epub import EpubBook, EpubHtml

def convert_to_epub(folder_path):
  """
  Converts .txt and .docx files in a given folder to .epub files.

  Args:
    folder_path: The path to the folder containing the files.

  Returns:
    None
  """

  for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    # Check if the file is a .txt or .docx file
    if filename.endswith((".txt", ".docx")):
      
      # Create an EPUB book
      book = EpubBook()
      book.set_title(filename[:-4])  # Remove the extension from the title
      
      # Create the HTML content for the EPUB file
      if filename.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
          content = f.read()
        html = EpubHtml(title=filename[:-4], file_name="content.xhtml", content=content)
      elif filename.endswith(".docx"):
        content = docx2txt.process(file_path)
        html = EpubHtml(title=filename[:-5], file_name="content.xhtml", content=content)
      
      # Add the HTML content to the EPUB book
      book.add_item(html)
      
      # Add the necessary navigation elements
      book.add_item(epub.EpubNcx())
      book.add_item(epub.EpubNav())
      
      # Set the language and cover image (optional)
      book.set_language('en')
      # book.set_cover("images/cover.jpg")
      
      # Write the EPUB file
      epub.write_epub(filename[:-4] + ".epub", book, {})
      
      print(f"{filename} converted to {filename[:-4]}.epub")

# Set the input folder path
input_folder_path = r"E:\ChatBot Therapy\Marcus Aurelius\Modern Stoic Book\The Main Book Sub Conscious Stoic\Full Book\TEXT"  # Replace with your actual folder path

# Convert files in the specified folder
convert_to_epub(input_folder_path)