import os
import pydub

def process_audio_files(root_folder):
    for folder in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder)
        
        if os.path.isdir(folder_path):
            # Create "2s Added" folder
            output_folder = os.path.join(folder_path, "2s Added")
            os.makedirs(output_folder, exist_ok=True)
            
            # Look for the "Audio" folder
            audio_folder = os.path.join(folder_path, "Audio")
            
            if os.path.exists(audio_folder):
                for filename in os.listdir(audio_folder):
                    if filename.endswith(".mp3"):
                        # Construct the full path to the file
                        file_path = os.path.join(audio_folder, filename)
                        
                        # Load the audio file using pydub
                        audio = pydub.AudioSegment.from_mp3(file_path)
                        
                        # Create silence segments
                        start_silence = pydub.AudioSegment.silent(duration=500)  # 0.5 second silence
                        end_silence = pydub.AudioSegment.silent(duration=2500)  # 2.5 seconds silence
                        
                        # Append silence to the beginning and end
                        audio_with_silence = start_silence + audio + end_silence
                        
                        # Output the modified audio file to the "2s Added" folder
                        output_file_path = os.path.join(output_folder, filename)
                        audio_with_silence.export(output_file_path, format="mp3")
                        
                        print(f"Added 0.5 second silence at the beginning and 2.5 seconds at the end of {filename}")

# Set the root folder path
root_folder = r"E:\Python_Practice\Text Separator\New Quotes List"

# Process the audio files
process_audio_files(root_folder)