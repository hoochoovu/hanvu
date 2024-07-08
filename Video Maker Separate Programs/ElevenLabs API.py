import requests
import json
import os
import chardet
import time

# Define constants for the script
CHUNK_SIZE = 1024
XI_API_KEY = "ELEVEN LABS API KEY" 
VOICE_ID = "VOICE ID" 
OUTPUT_FOLDER = r"E:\Python_Practice\Text Separator\Blog Output"  # Folder to save output audio files
TEXT_FOLDER = r"E:\Python_Practice\Text Separator\Blog Text"  # Folder to read text files

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Construct the URL for the Text-to-Speech API request
tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

# Set up headers for the API request, including the API key for authentication
headers = {
    "Accept": "application/json",
    "xi-api-key": XI_API_KEY
}

# Main loop to process text files in the folder
while True:
    # Get list of .txt files in the folder
    text_files = [f for f in os.listdir(TEXT_FOLDER) if f.endswith(".txt")]

    # If no files found, sleep for 5 seconds and continue
    if not text_files:
        print("No text files found. Waiting for 5 seconds...")
        time.sleep(5)
        break

    # Iterate through each .txt file
    for text_file in text_files:
        # Construct the full path to the text file
        text_path = os.path.join(TEXT_FOLDER, text_file)

        # Read the text file and store the content with encoding detection
        with open(text_path, 'rb') as f:
            data = f.read()
            encoding = chardet.detect(data)['encoding']  # Detect encoding
            
            with open(text_path, "r", encoding=encoding) as f:  # Read with detected encoding
                TEXT_TO_SPEAK = f.read()

        # Set up the data payload for the API request
        data = {
            "text": TEXT_TO_SPEAK,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        # Make the POST request to the TTS API with headers and data, enabling streaming response
        response = requests.post(tts_url, headers=headers, json=data, stream=True)

        # Check if the request was successful
        if response.ok:
            # Create a unique filename for the output audio file
            output_filename = f"{os.path.splitext(text_file)[0]}.mp3"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            # Open the output file in write-binary mode
            with open(output_path, "wb") as f:
                # Read the response in chunks and write to the file
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)
            # Inform the user of success
            print(f"Audio stream saved successfully to: {output_path}")

            # Move the processed text file to a "processed" folder (optional)
            processed_folder = "processed_text"
            os.makedirs(processed_folder, exist_ok=True)
            os.rename(text_path, os.path.join(processed_folder, text_file))
        else:
            # Print the error message if the request was not successful
            print(response.text)

        # Wait for 1 second before processing the next file
        time.sleep(1)