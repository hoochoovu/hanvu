import os
import textwrap

def format_text(text):
    # Split the text into content and author
    content, _, author = text.rpartition('-')
    
    # Wrap the content
    wrapped_content = textwrap.fill(content.strip(), width=25, break_long_words=False)
    
    # Remove leading spaces from each line
    formatted_content = '\n'.join(line.lstrip() for line in wrapped_content.split('\n'))
    
    # Format the author
    formatted_author = f"\n\n- {author.strip()}" if author else ""
    
    return formatted_content + formatted_author

def process_files(input_folder):
    for subfolder in os.listdir(input_folder):
        subfolder_path = os.path.join(input_folder, subfolder)
        
        if os.path.isdir(subfolder_path):
            text_subfolder = os.path.join(subfolder_path, 'Text')
            
            if os.path.exists(text_subfolder):
                for filename in os.listdir(text_subfolder):
                    if filename.endswith('.txt'):
                        input_path = os.path.join(text_subfolder, filename)
                        output_path = os.path.join(subfolder_path, filename)  

                        with open(input_path, 'r', encoding='utf-8') as file:
                            text = file.read()
                        
                        formatted_text = format_text(text)
                        
                        with open(output_path, 'w', encoding='utf-8') as file:
                            file.write(formatted_text)

# Example usage
input_folder = r"E:\Python_Practice\Text Separator\New Quotes List\Thich Nhat Hanh"  # Replace with your input folder path
process_files(input_folder)