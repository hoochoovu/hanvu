import os
import random
import subprocess
from datetime import datetime
import logging

# Setup logging configuration
logging.basicConfig(filename='video_processing.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def insert_video_metadata(video_path, title, artist, genre, copyright, description):
    """Inserts metadata into the video file using ffmpeg."""
    command = [
        "ffmpeg", "-i", video_path,
        "-metadata", f"title={title}",
        "-metadata", f"artist={artist}",
        "-metadata", f"genre={genre}",
        "-metadata", f"copyright={copyright}",
        "-metadata", f"description={description}",
        "-codec:v", "copy", "-codec:a", "copy",  # Copy video and audio streams without re-encoding
        "-y", f"{os.path.splitext(video_path)[0]}_metadata.mp4"  # Output file with metadata
    ]
    subprocess.run(command, check=True)
    logging.info(f"Metadata inserted into video: {video_path}")

    # Replace the original video with the one containing metadata
    os.replace(f"{os.path.splitext(video_path)[0]}_metadata.mp4", video_path)

def try_remove_file(filepath):
    """Attempts to remove a file if it exists."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logging.info(f"Removed existing file: {filepath}")
        else:
            logging.info(f"No existing file to remove at: {filepath}")
    except Exception as e:
        logging.error(f"Error removing file {filepath}: {e}")

# Attempt to remove the temporary final video file at the start
try_remove_file(os.path.join("output", "final_video_1.mp4"))

QUALITY_SETTINGS = {
    "Default": "2000k",
    "High": "4000k",
    "Higher": "6000k",
    "Intense": "8000k",
    "Extreme": "10000k"
}

def get_video_info(video_path):
    """Retrieve video width and height using ffprobe."""
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                           "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", video_path],
                          capture_output=True, text=True).stdout.strip().split('x')
    return int(info[0]), int(info[1])

def get_video_duration(video_path):
    """Retrieve video duration using ffprobe."""
    duration = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                               "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                              capture_output=True, text=True).stdout.strip()
    return float(duration)

def trim_video_to_duration(input_video, output_video, duration, gpu_device=1):
    """Trims the video to the specified duration, using the specified GPU device."""
    command = [
        "ffmpeg", "-hwaccel", "cuda", "-hwaccel_device", str(gpu_device), "-i", input_video, 
        "-t", str(duration), "-c:v", "copy", "-c:a", "copy", 
        "-y", output_video
    ]
    subprocess.run(command, check=True)
    logging.info(f"Trimmed video {input_video} to {duration} seconds, saved as {output_video}")

def select_random_video_without_reuse(folder, used_videos):
    """Selects a random video from a folder, ensuring no duplicates."""
    videos = [os.path.join(root, file)
              for root, _, files in os.walk(folder)
              for file in files if file.endswith(".mp4") and os.path.join(root, file) not in used_videos]
    
    if not videos:
        raise FileNotFoundError(f"No more unused videos found in {folder}. All videos have been used.")
    
    selected_video = random.choice(videos)
    ##used_videos.add(selected_video) ## USED VIDEOS DON'T GET ADDED HERE ##
    return selected_video

def ensure_bg_videos_for_duration(duration_folder, required_duration, gpu_device=0):
    """Ensure one random background video loops continuously until the required duration is met."""
    used_videos = set()
    selected_video = select_random_video_without_reuse(duration_folder, used_videos)
    video_duration = get_video_duration(selected_video)

    if video_duration == 0:
        raise ValueError(f"Video {selected_video} has zero duration.")

    # Create a list of the background video to fill the required duration by looping a single video
    bg_videos = [selected_video]  # Only use this single video
    total_duration = video_duration

    # If the video duration is shorter than required, loop it until the total duration is met
    while total_duration < required_duration:
        total_duration += video_duration

    # Trim the final loop to perfectly match the required duration
    remaining_duration = required_duration - (total_duration - video_duration)
    if remaining_duration > 0:
        trimmed_video = os.path.join(os.path.dirname(selected_video), "trimmed_bg.mp4")
        trim_video_to_duration(selected_video, trimmed_video, remaining_duration)
        bg_videos.append(trimmed_video)

    return bg_videos, selected_video


def merge_videos(bg_paths, fg_path, output_video_path, zoom=1.0, x_offset=0, y_offset=0, quality="Default", gpu_device=0):
    """Merges background and foreground videos using color keying, applying zoom and offsets, while retaining audio."""
    logging.info(f"Merging videos with foreground: {fg_path} and background: {bg_paths[0]}")

    try:
        fg_width, fg_height = get_video_info(fg_path)
        bg_width, bg_height = get_video_info(bg_paths[0])  # Only one video selected

        # Adjust offsets for centering the foreground video
        scaled_fg_width = int(fg_width * zoom)
        scaled_fg_height = int(fg_height * zoom)
        x_center_offset = (bg_width - scaled_fg_width) // 2 + x_offset
        y_center_offset = (bg_height - scaled_fg_height) // 2 + y_offset

        bitrate = QUALITY_SETTINGS.get(quality, "2000k")  # Default to "2000k" if quality not found

        # Loop background video to match the required duration
        looped_bg_command = [
            "ffmpeg", "-hwaccel", "cuda", "-hwaccel_device", str(gpu_device), 
            "-stream_loop", "-1", "-i", bg_paths[0],  # Loop the background video infinitely
            "-i", fg_path,
            "-filter_complex",
            f"[1:v]colorkey=0x000000:0.1:0.1,scale={scaled_fg_width}:{scaled_fg_height}[fg];"
            f"[0:v][fg]overlay=x={x_center_offset}:y={y_center_offset}[video]",
            "-map", "[video]", "-map", "1:a?",  # Include the audio from the foreground video if it exists
            "-c:v", "h264_nvenc", "-preset", "slow", "-b:v", bitrate, "-c:a", "aac", "-b:a", "192k",
            "-y", output_video_path
        ]

        result = subprocess.run(looped_bg_command, capture_output=True, text=True)
        logging.info(f"FFmpeg output:\n{result.stdout}")
        logging.error(f"FFmpeg errors:\n{result.stderr}")
    except Exception as e:
        logging.error(f"Error during video merging: {e}")
        raise

def select_random_audio(folder, used_audios):
    """Selects a random audio file from a folder."""
    audios = [os.path.join(folder, f) for f in os.listdir(folder)
              if (f.endswith(".mp3") or f.endswith(".wav")) and os.path.join(folder, f) not in used_audios]
    if not audios:
        raise FileNotFoundError(f"No unused audio files found in {folder}.")
    selected_audio = random.choice(audios)
    used_audios.add(selected_audio)
    return selected_audio

def merge_audio_to_video(video_path, bg_music, bg_music_volume=0, final_audio_volume=0, used_audios=set()):
    """Merges background music into a video and returns the output path."""
    logging.info(f"Merging audio to video: {video_path} with background music: {bg_music}")
    
    video_duration = get_video_duration(video_path)

    if os.path.isdir(bg_music):
        bg_music_path = select_random_audio(bg_music, used_audios)
    else:
        bg_music_path = bg_music

    # Create background music looped to video duration
    looped_audio_path = "looped_audio.wav"
    subprocess.run(["ffmpeg", "-stream_loop", "-1", "-i", bg_music_path, "-t", str(video_duration), "-y", looped_audio_path], check=True)

    # Merge the video with the looped background music
    output_video_path = f"{os.path.splitext(video_path)[0]}_with_audio.mp4"
    command = [
        "ffmpeg", "-hwaccel", "cuda", "-i", video_path, "-i", looped_audio_path,
        "-filter_complex", f"[1:a]volume={bg_music_volume}dB[aud];[0:a][aud]amix=inputs=2:duration=first[a];"
                           f"[a]volume={final_audio_volume}dB[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-y", output_video_path
    ]
    subprocess.run(command, check=True)
    
    # Cleanup intermediate files
    os.remove(looped_audio_path)

    return output_video_path

def create_final_video_sequence(bg_folder, fg_folder, title_folder, author_folder, stoistica_folder, book_folder, output_folder, duration, iterations, quality, bg_music, bg_music_volume, final_audio_volume, altbg_category=None):
    """Creates the final video sequence by combining title, background, and foreground videos with audio."""
    
    duration_folders = {
        59: "smoke",
        90: "smoke",
        599: "smoke",
        30 * 60: "smoke",  
        60 * 60: "smoke",
        40271: "smoke"   
    }

    duration_labels = {
        59: "[1m]",
        90: "[2m]",
        599: "[10m]",
        30 * 60: "[30m]",
        60 * 60: "[60m]",
        40271: "[11Hours]"
    }

    if duration not in duration_folders:
        raise ValueError("Unsupported duration value")

    # Get the label for the duration, or use [Custom] if it's not predefined
    duration_label = duration_labels.get(duration, "[Custom]")

    os.makedirs(output_folder, exist_ok=True)
    duration_folder = os.path.join(bg_folder, duration_folders[duration])

    # Prepare alternative background folder if selected
    altbg_folder = os.path.join(bg_folder, altbg_category) if altbg_category else None

    used_videos = set()
    used_audios = set()

    for i in range(iterations):
        try:
            logging.info(f"Starting iteration {i+1} of {iterations}")

            # Select and merge background videos without duplication
            bg_videos = []
            total_bg_duration = 0
            alternate = False  # Flag to alternate between regular and alternative backgrounds

            while total_bg_duration < duration:
                if altbg_folder and alternate:
                    selected_video = select_random_video_without_reuse(altbg_folder, used_videos)
                else:
                    selected_video = select_random_video_without_reuse(duration_folder, used_videos)
                
                bg_videos.append(selected_video)
                total_bg_duration += get_video_duration(selected_video)
                alternate = not alternate  # Toggle the flag for next selection

            # Select title video
            title_video_path = select_random_video_without_reuse(title_folder, used_videos)
            video_sequence = [title_video_path]  # Start with title video

            # Build the video sequence in the new order: FG, FG, Stoistica, FG, FG, Author, Book
            folders_sequence = [fg_folder, fg_folder, stoistica_folder, fg_folder, fg_folder, author_folder, book_folder]
            total_duration = get_video_duration(title_video_path)

            while total_duration < duration:
                for folder in folders_sequence:
                    if total_duration >= duration:
                        break
                    fg_video_path = select_random_video_without_reuse(folder, used_videos)
                    video_sequence.append(fg_video_path)
                    total_duration += get_video_duration(fg_video_path)

            # Concatenate the video sequence into a single video file
            with open("concat_list.txt", "w") as f:
                for video_path in video_sequence:
                    f.write(f"file '{video_path}'\n")

            final_video_path = os.path.join(output_folder, f"final_video_{i+1}.mp4")
            command = [
                "ffmpeg", "-f", "concat", "-safe", "0", "-i", "concat_list.txt",
                "-c:v", "h264_nvenc", "-preset", "slow", "-y", final_video_path
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            logging.info(f"FFmpeg output: {result.stdout}")
            logging.error(f"FFmpeg errors: {result.stderr}")

            # Merge background videos
            final_output_path = os.path.join(output_folder, f"final_output_{i}.mp4")
            merge_videos(bg_videos, final_video_path, final_output_path, quality=quality)

            # Merge audio
            output_video_with_audio = merge_audio_to_video(final_output_path, bg_music, bg_music_volume, final_audio_volume, used_audios)

            # Ensure the final video duration does not exceed the set duration
            trimmed_output_path = os.path.join(output_folder, f"final_video_trimmed_{i}.mp4")
            trim_video_to_duration(output_video_with_audio, trimmed_output_path, duration)

            # Add duration and altbg_category to the final file name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            altbg_label = f"[{altbg_category}]" if altbg_category else ""
            
            # Construct the final name
            final_name = os.path.join(
                output_folder, 
                f"{duration_label}{altbg_label}Motivational_Quotes_Video_{timestamp}_{i}.mp4"
            )
            os.rename(trimmed_output_path, final_name)

            # Insert metadata
            insert_video_metadata(
                final_name,
                title="Motivational Quotes Video for Work Out and Exercise",  # Replace with your desired title
                artist="Stoistica",  # Replace with your artist/channel name
                genre="Motivational",  # Replace with the appropriate genre
                copyright="Stoistica Copyright 2024",  # Replace with your copyright information
                description="Motivational Quotes Video for sleep, work out, inspiration - philosophy, stoicism, wisdom quote,"  # Replace with your video description
            )

            # Cleanup
            os.remove(final_video_path)
            os.remove(final_output_path)
            os.remove(output_video_with_audio)
            os.remove("concat_list.txt")

            logging.info(f"Final video created: {final_name}")
            print(f"Final video created: {final_name}")

        except Exception as e:
            logging.error(f"Error during iteration {i+1}: {e}")
            print(f"Error during iteration {i+1}: {e}")

if __name__ == "__main__":
    bg_folder = r"I:\IntelDrive Dataset\Samurai 11 Hour Videos"
    fg_folder = r"E:\Dataset\All Audio Quotes\Video Clips (Full Letters)\Horizontal\Golden 2s Added"
    title_folder = r"E:\Dataset\All Authors - 44.1khz\Test Horizontal (44.1khz)"
    author_folder = r"E:\Dataset\All Authors - 44.1khz\Test Horizontal (44.1khz)"
    stoistica_folder = r"E:\Dataset\All STOISTICA Audio\Video Clips\Horizontal\2s Added"
    book_folder = r"E:\Dataset\All Audiobook\Horizontal"
    bg_music = r"E:\Dataset\ALL BG Music\Long Sub-Conscious Sleep Music"
    output_folder = r"output\Book Outputs"

    duration = 30 * 60  # Options: duration in seconds (e.g., 59, 90, 599, 30 * 60, 60 * 60, 40271)
    iterations = 1  # Number of iterations to generate
    quality = "Extreme"  # Options: "Default", "High", "Higher", "Intense", "Extreme"
    bg_music_volume = -3  # Volume adjustment in decibels, 0 is default, negative values reduce volume
    final_audio_volume = 9  # in dB
    altbg_category = "smoke"  # Replace with "Exercise", "Hiking", "Ocean", "God", "Monk", "Rock", "Time", "Stoic", "Random", or None
    # Only 10m videos can choose a category. If video is less than 599, it will always be randomized background.
    
    create_final_video_sequence(
        bg_folder, fg_folder, title_folder, author_folder, stoistica_folder, book_folder, 
        output_folder, duration, iterations, quality, bg_music, 
        bg_music_volume, final_audio_volume, altbg_category
    )