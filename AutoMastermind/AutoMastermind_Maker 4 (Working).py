import os
import shutil
import time
import chardet
from pydub import AudioSegment
import requests
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- Configuration ---

# Gemini
GEMINI_API_KEY = "id_key"
GEMINI_MODEL = "gemini-1.5-flash"
CUSTOM_PROMPT_FILE = "prompt.txt"

# ElevenLabs
XI_API_KEY = "id_key"
VOICE_IDS = {
    "Zeno.txt": "pzrhJDAsvLBKznXczPvF",
    "Stoic_Philosopher.txt": "GRxyBIYvuPkKIpWjqzA2",
    "Zen_Monk.txt": "LipOM79LKgtTo7mSJlVl"
}

# Folders
TEMP_FOLDER = r"E:\Python_Practice\AutoMastermind\TEMP"
WORK_FOLDER = r"E:\Python_Practice\AutoMastermind\WORK"
GEMINI_TEXT_FOLDER = "Gemini_Text"
PROCESSED_TEXT_FOLDER = "Processed_Text"
SEPARATED_TEXT_FOLDER = "Separated_Text"
PROCESSED_SEPARATED_FOLDER = "Sep_Finished"
OUTPUT_AUDIO_FOLDER = "11LABS_OUTPUT"
FINAL_AUDIO_FOLDER = "FINAL_AUDIO"

# Audio settings
CHUNK_SIZE = 1024

# --- Functions ---

def configure_gemini():
    """Configures the Gemini API."""
    genai.configure(api_key=GEMINI_API_KEY)

def generate_gemini_text(filepath, custom_prompt_file):
    global audio_filename  # Declare that you're using the global variable
    """Generates text content using Gemini."""
    with open(filepath, "r", encoding='utf-8') as f:
        file_content = f.read()
    with open(custom_prompt_file, "r", encoding='utf-8') as f:
        custom_prompt = f.read()

    prompt = f"{file_content}\n\n{custom_prompt}"

    model = genai.GenerativeModel(GEMINI_MODEL)
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
    audio_filename = output_filename
    output_filepath = os.path.join(GEMINI_TEXT_FOLDER, output_filename)

    with open(output_filepath, "w", encoding='utf-8') as f:
        f.write(response.text)

    os.remove(filepath)

    # Move processed file to "Processed" folder
    #shutil.move(filepath, os.path.join(PROCESSED_TEXT_FOLDER, output_filename))

def parse_commentary(file_path, output_folder, processed_folder):
    """Parses a .txt file into three separate files based on the [Text] sections."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

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

def process_text_file(text_file):
    """Generates audio from a text file using ElevenLabs."""
    text_path = os.path.join(SEPARATED_TEXT_FOLDER, text_file)

    # Read the text file with encoding detection
    with open(text_path, 'rb') as f:
        data = f.read()
        encoding = chardet.detect(data)['encoding']
        with open(text_path, "r", encoding=encoding) as f:
            text_to_speak = f.read()

    voice_id = VOICE_IDS.get(text_file)
    if not voice_id:
        print(f"No voice ID found for {text_file}. Skipping...")
        return

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }
    data = {
        "text": text_to_speak,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    if response.ok:
        output_filename = f"{os.path.splitext(text_file)[0]}.mp3"
        output_path = os.path.join(OUTPUT_AUDIO_FOLDER, output_filename)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)

        print(f"Audio stream saved successfully to: {output_path}")

        os.remove(text_path)
        # Move the text file (optional)
        #os.makedirs(PROCESSED_TEXT_FOLDER, exist_ok=True)
        #os.rename(text_path, os.path.join(PROCESSED_TEXT_FOLDER, text_file))

    else:
        print(response.text)

    time.sleep(1)

def combine_audio(filenames):
    """Combines multiple audio files into a single file."""
    combined_audio = AudioSegment.empty()
    for filename in filenames:
        audio_file = os.path.join(OUTPUT_AUDIO_FOLDER, filename)
        segment = AudioSegment.from_mp3(audio_file)
        combined_audio += segment

    output_filename = audio_filename + ".mp3"
    output_path = os.path.join(FINAL_AUDIO_FOLDER, output_filename)
    combined_audio.export(output_path, format="mp3")

    print(f"Audio files combined and saved to: {output_path}")

    # Remove the original audio files after combining
    for filename in filenames:
        audio_file = os.path.join(OUTPUT_AUDIO_FOLDER, filename)
        os.remove(audio_file)

    # Move the processed audio files to a "processed" folder
    #processed_audio_folder = "processed_audio"
    #os.makedirs(processed_audio_folder, exist_ok=True)
    #for filename in filenames:
    #    audio_path = os.path.join(OUTPUT_AUDIO_FOLDER, filename)
    #    os.rename(audio_path, os.path.join(processed_audio_folder, filename))

def create_output_folders():
    """Creates the output folders."""
    os.makedirs(OUTPUT_AUDIO_FOLDER, exist_ok=True)
    os.makedirs(FINAL_AUDIO_FOLDER, exist_ok=True)
    os.makedirs(GEMINI_TEXT_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_TEXT_FOLDER, exist_ok=True)
    os.makedirs(SEPARATED_TEXT_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_SEPARATED_FOLDER, exist_ok=True)

def main():
    """Main function to orchestrate the process."""
    configure_gemini()
    create_output_folders()

    while True:
        # 0. Process text files from the Temp folder to the work folder
        for filename in os.listdir(TEMP_FOLDER):
            if filename.endswith((".txt", ".md", ".html", ".json", ".csv")):
                filepath = os.path.join(TEMP_FOLDER, filename)
                shutil.move(filepath, WORK_FOLDER)  # Move to WORK folder after processing
                    
            # 1. Process initial text files with Gemini
            for filename in os.listdir(WORK_FOLDER):
                if filename.endswith((".txt", ".md", ".html", ".json", ".csv")):
                    filepath = os.path.join(WORK_FOLDER, filename)
                    generate_gemini_text(filepath, CUSTOM_PROMPT_FILE)

            # 2. Process separated text files
            for filename in os.listdir(GEMINI_TEXT_FOLDER):
                if filename.endswith(".txt"):
                    file_path = os.path.join(GEMINI_TEXT_FOLDER, filename)
                    parse_commentary(file_path, SEPARATED_TEXT_FOLDER, PROCESSED_SEPARATED_FOLDER)

            # 3. Generate audio from processed text files
            while True:
                text_files = [f for f in os.listdir(SEPARATED_TEXT_FOLDER) if f.endswith(".txt")]
                if not text_files:
                    print("No text files found. Waiting for 5 seconds...")
                    time.sleep(5)
                    break # Break the loop if no files found.

                for text_file in text_files:
                    process_text_file(text_file)

            # 4. Combine audio files
            filenames = ["Zeno.mp3", "Stoic_Philosopher.mp3", "Zen_Monk.mp3"]
            combine_audio(filenames)

if __name__ == "__main__":
    main()