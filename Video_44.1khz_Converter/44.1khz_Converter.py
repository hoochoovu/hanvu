import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def convert_audio(input_file, output_file):
    command = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "copy",  # Copy the video stream without re-encoding
        "-ar", "44100",  # Set the audio sample rate to 44.1kHz
        "-y",  # Overwrite output file if it exists
        output_file
    ]
    
    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE)
        print(f"Successfully converted: {input_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}: {e.stderr.decode()}")

def process_videos(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = []
        for video_file in video_files:
            input_path = os.path.join(input_folder, video_file)
            output_path = os.path.join(output_folder, f"{name}_{video_file}")
            futures.append(executor.submit(convert_audio, input_path, output_path))

        for future in as_completed(futures):
            future.result()  # This will raise any exceptions that occurred during execution

if __name__ == "__main__":
    name = "Miyamoto Musashi - The Path of Aloneness - Hungry 44.1kHz "
    input_folder = r"input"
    output_folder = r"output"
    
    process_videos(input_folder, output_folder)
    print("All conversions completed.")