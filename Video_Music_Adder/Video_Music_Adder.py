import os
import random
import subprocess
from datetime import datetime

def get_video_duration(video_path):
    """Retrieve video duration using ffprobe."""
    duration = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                               "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                              capture_output=True, text=True).stdout.strip()
    return float(duration)

def select_random_audio(folder):
    """Selects a random audio file from a folder."""
    audios = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".mp3") or f.endswith(".wav")]
    return random.choice(audios) if audios else None

def merge_audio_to_video(input_folder, output_folder, bg_music, bg_music_volume=0):
    """Merges background music into each video in the input folder and saves to the output folder."""
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"Input folder not found: {input_folder}")
    
    os.makedirs(output_folder, exist_ok=True)
    videos = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".mp4")]
    
    for video in videos:
        video_duration = get_video_duration(video)
        
        if os.path.isdir(bg_music):
            bg_music_path = select_random_audio(bg_music)
            if not bg_music_path:
                raise FileNotFoundError("No audio files found in the specified folder.")
        else:
            bg_music_path = bg_music

        # Create background music looped to video duration
        looped_audio_path = os.path.join(output_folder, "looped_audio.wav")
        subprocess.run(["ffmpeg", "-stream_loop", "-1", "-i", bg_music_path, "-t", str(video_duration), "-y", looped_audio_path], check=True)

        # Merge the video with the looped background music
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_video_path = os.path.join(output_folder, f"{os.path.basename(video).split('.')[0]}_with_audio_{timestamp}.mp4")
        command = [
            "ffmpeg", "-hwaccel", "cuda", "-i", video, "-i", looped_audio_path,
            "-filter_complex", f"[1:a]volume={bg_music_volume}dB[aud];[0:a][aud]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-y", output_video_path
        ]
        subprocess.run(command, check=True)
        
        # Cleanup intermediate files
        os.remove(looped_audio_path)
        print(f"Processed video: {output_video_path}")

if __name__ == "__main__":
    input_folder = "input"  # Update this path as needed
    output_folder = "output"  # Update this path as needed
    bg_music = r"E:\Dataset\ALL BG Music\I Am a Man Who Will Fight for Your Honor.mp3"  # Can be a folder or a file path
    bg_music_volume = -10  # Volume adjustment in decibels, 0 is default, negative values reduce volume

    merge_audio_to_video(input_folder, output_folder, bg_music, bg_music_volume)
