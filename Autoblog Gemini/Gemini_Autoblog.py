import requests
import os
import subprocess
import random
import shutil
import json
import datetime
import chardet
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- Configuration ---
INPUT_FOLDER = "Input"
OUTPUT_TEXT_FOLDER = "Output_Text"
PROCESSED_FOLDER = "Processed"
CUSTOM_PROMPT_FILE = "prompt.txt"

# --- Text Content Generation ---

def generate_text_content(filepath, custom_prompt_file):
    """Generates text content using Gemini and saves it to a file."""

    # Read custom prompt from file
    with open(custom_prompt_file, "r", encoding='utf-8') as f:
        custom_prompt = f.read()

    # Gemini processing
    genai.configure(api_key = "id_key")
    model = genai.GenerativeModel('gemini-1.5-flash')

    with open(filepath, "r", encoding='utf-8') as f:
        file_content = f.read()
    prompt = f"{file_content}\n\n{custom_prompt}"
    response = model.generate_content(
        prompt,
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )

    output_filename = f"[Original]-{os.path.basename(filepath)}"
    output_filepath = os.path.join(OUTPUT_TEXT_FOLDER, output_filename)

    with open(output_filepath, "w", encoding='utf-8') as f:
        f.write(response.text)
    print(f"Processed file: {os.path.basename(filepath)}")

    # Move processed file to "Processed" folder
    shutil.move(filepath, os.path.join(PROCESSED_FOLDER, output_filename))


# --- Main Function ---

def main():
    """Processes input files and generates text content and images."""

    # Create output folders if they don't exist
    os.makedirs(OUTPUT_TEXT_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)

    # Process text files
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith((".txt", ".md", ".html", ".json", ".csv")):
            filepath = os.path.join(INPUT_FOLDER, filename)
            generate_text_content(filepath, CUSTOM_PROMPT_FILE)

if __name__ == "__main__":
    main()