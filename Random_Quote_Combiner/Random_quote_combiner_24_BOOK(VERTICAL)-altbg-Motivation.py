import os
import random
import subprocess
from datetime import datetime
import logging

# Set the GPU ID to use
gpu_id = 0  # Change this to select a different GPU (0, 1, etc.)
os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

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

def trim_video_to_duration(input_video, output_video, duration):
    """Trims the video to the specified duration."""
    command = [
        "ffmpeg", "-hwaccel", "cuda", "-i", input_video, 
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
    used_videos.add(selected_video)
    return selected_video

def ensure_unique_bg_videos(duration_folder, used_videos, required_duration):
    """Select background videos without duplication to meet or exceed the required duration."""
    total_bg_duration = 0
    bg_videos = []
    
    while total_bg_duration < required_duration:
        if not used_videos:
            logging.info("All background videos have been used. Starting fresh with a new loop.")
        try:
            next_bg_video = select_random_video_without_reuse(duration_folder, used_videos)
            bg_videos.append(next_bg_video)
            total_bg_duration += get_video_duration(next_bg_video)
        except FileNotFoundError:
            logging.warning("All background videos have been used once. Resetting and continuing.")
            used_videos.clear()  # Clear the set to allow videos to be reused
        
    if total_bg_duration < required_duration:
        logging.warning(f"Could not find enough unique videos to meet duration requirement. Current duration: {total_bg_duration}")

    return bg_videos

def merge_videos(bg_paths, fg_path, output_video_path, zoom=1.0, x_offset=0, y_offset=0, quality="Default"):
    """Merges background and foreground videos using color keying, applying zoom and offsets, while retaining audio."""
    logging.info(f"Merging videos with foreground: {fg_path} and backgrounds: {bg_paths}")
    
    try:
        fg_width, fg_height = get_video_info(fg_path)
        bg_width, bg_height = get_video_info(bg_paths[0])  # Assume all background videos have the same resolution
        
        # Adjust offsets for centering the foreground video
        scaled_fg_width = int(fg_width * zoom)
        scaled_fg_height = int(fg_height * zoom)
        x_center_offset = (bg_width - scaled_fg_width) // 2 + x_offset
        y_center_offset = (bg_height - scaled_fg_height) // 2 + y_offset

        bitrate = QUALITY_SETTINGS.get(quality, "2000k")  # Default to "2000k" if quality not found

        # Concatenate background videos if multiple
        if len(bg_paths) > 1:
            with open("bg_concat_list.txt", "w") as f:
                for bg_path in bg_paths:
                    f.write(f"file '{bg_path}'\n")
            
            bg_concat_path = "concatenated_bg.mp4"
            command = [
                "ffmpeg", "-f", "concat", "-safe", "0", "-i", "bg_concat_list.txt",
                "-c:v", "copy", "-y", bg_concat_path
            ]
            subprocess.run(command, check=True)
        else:
            bg_concat_path = bg_paths[0]

        # Build ffmpeg command for video merging, including audio from the foreground video
        command = [
            "ffmpeg", "-hwaccel", "cuda", "-i", bg_concat_path, "-i", fg_path,
            "-filter_complex",
            f"[1:v]colorkey=0x000000:0.1:0.1,scale={scaled_fg_width}:{scaled_fg_height}[fg];"
            f"[0:v][fg]overlay=x={x_center_offset}:y={y_center_offset}[video]",
            "-map", "[video]", "-map", "1:a?",  # Include the audio from the foreground video if it exists
            "-c:v", "h264_nvenc", "-preset", "slow", "-b:v", bitrate, "-c:a", "aac", "-b:a", "192k",
            "-y", output_video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        logging.info(f"FFmpeg output:\n{result.stdout}")
        logging.error(f"FFmpeg errors:\n{result.stderr}")
    except Exception as e:
        logging.error(f"Error during video merging: {e}")
        raise

    # Cleanup
    if len(bg_paths) > 1:
        os.remove(bg_concat_path)
        os.remove("bg_concat_list.txt")

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
    """Merges background music into a video and returns the output path and first two words of the audio file name."""
    logging.info(f"Merging audio to video: {video_path} with background music: {bg_music}")
    
    video_duration = get_video_duration(video_path)

    if os.path.isdir(bg_music):
        bg_music_path = select_random_audio(bg_music, used_audios)
    else:
        bg_music_path = bg_music

    # Extract first two words from the audio file name
    audio_file_name = os.path.basename(bg_music_path)
    first_two_words = ' '.join(audio_file_name.split()[:2])

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

    return output_video_path, first_two_words


def create_final_video_sequence(bg_folder, fg_folder, title_folder, author_folder, stoistica_folder, book_folder, motivation_folder, output_folder, duration, iterations, quality, bg_music, bg_music_volume, final_audio_volume, altbg1_folder, altbg2_folder, altbg3_folder, altbg4_folder):
    """Creates the final video sequence with the new folder and alternating altbg logic."""
    
    duration_folders = {
        59: "1 Minute",
        90: "1 Minute",
        599: "2 Minute",
        30 * 60: "2 Minute",  
        60 * 60: "2 Minute",
        23795: "2 Minute",
        28799: "2 Minute",
        32948: "2 Minute",
        40270: "2 Minute"   
    }

    duration_labels = {
        59: "[1m]",
        90: "[2m]",
        599: "[10m]",
        30 * 60: "[30m]",
        60 * 60: "[60m]",
        23795: "[6Hours]",
        28799: "[8Hours]",
        32948: "[9Hours]",
        40270: "[11Hours]"
    }

    if duration not in duration_folders:
        raise ValueError("Unsupported duration value")

    # Get the label for the duration, or use [Custom] if it's not predefined
    duration_label = duration_labels.get(duration, "[Custom]")

    os.makedirs(output_folder, exist_ok=True)
    duration_folder = os.path.join(bg_folder, duration_folders[duration])

    used_videos = set()  # Track already used videos
    used_audios = set()  # Track already used audio files

    for i in range(iterations):
        try:
            logging.info(f"Starting iteration {i+1} of {iterations}")
            
            # Select and merge background videos
            bg_videos = []
            total_bg_duration = 0

            # Select from bg_folder first
            selected_video = select_random_video_without_reuse(bg_folder, used_videos)
            bg_videos.append(selected_video)
            total_bg_duration += get_video_duration(selected_video)

            # Now rotate between altbg1, altbg2, altbg3
            altbg_folders = [altbg1_folder, altbg2_folder, altbg3_folder, altbg4_folder]
            altbg_index = 0  # To track which altbg folder is currently in use

            # Loop to add videos from alternating altbg folders
            for _ in range(3):  # Control how many altbg videos you want to insert
                selected_altbg = altbg_folders[altbg_index]
                altbg_video = select_random_video_without_reuse(selected_altbg, used_videos)
                bg_videos.append(altbg_video)
                total_bg_duration += get_video_duration(altbg_video)
                altbg_index = (altbg_index + 1) % len(altbg_folders)  # Rotate through altbg folders

            # Check if total duration is met, continue selecting from bg_folder if needed
            while total_bg_duration < duration:
                next_bg_video = select_random_video_without_reuse(bg_folder, used_videos)
                bg_videos.append(next_bg_video)
                total_bg_duration += get_video_duration(next_bg_video)

            # Select title video
            title_video_path = select_random_video_without_reuse(title_folder, used_videos)
            video_sequence = [title_video_path]  # Start with title video

            # Build the video sequence in the new order: FG, FG, Stoistica, FG, FG, Author, Book, Motivation
            folders_sequence = [fg_folder, fg_folder, stoistica_folder, fg_folder, fg_folder, author_folder, book_folder, motivation_folder]
            total_duration = get_video_duration(title_video_path)

            # Add videos to the sequence until the total duration is met
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
            output_video_with_audio, first_two_words = merge_audio_to_video(final_output_path, bg_music, bg_music_volume, final_audio_volume, used_audios)

            # Ensure the final video duration does not exceed the set duration
            trimmed_output_path = os.path.join(output_folder, f"final_video_trimmed_{i}.mp4")
            trim_video_to_duration(output_video_with_audio, trimmed_output_path, duration)

            # Add duration, altbg_category, and first two words of audio file to the final file name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            altbg_label = f"[{altbg_category}]" if altbg_category else ""
            
            # Construct the final name
            final_name = os.path.join(
                output_folder, 
                f"{duration_label}{altbg_label}[{first_two_words}]Motivational_Quotes_Video_{timestamp}_{i}.mp4"
            )
            os.rename(trimmed_output_path, final_name)

            # Insert metadata
            insert_video_metadata(
                final_name,
                title="Motivational Quotes Video for Work Out and Exercise",  # Replace with your desired title
                artist="Stoistica",  # Replace with your artist/channel name
                genre="Motivational",  # Replace with the appropriate genre
                copyright="Stoistica 2024",  # Replace with your copyright information
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


def select_next_altbg_folder():
    """Selects the next altbg folder in round-robin manner."""
    global altbg_index
    selected_folder = altbg_folders[altbg_index]
    altbg_index = (altbg_index + 1) % len(altbg_folders)  # Rotate index between 0, 1, and 2
    return selected_folder

if __name__ == "__main__":
    bg_folder = r"E:\Dataset\All Video BG\Watermarked\Vertical"
    fg_folder = r"E:\Dataset\All Audio Quotes\Video Clips (Full Letters)\Vertical\2s Added"
    title_folder = r"E:\Dataset\All Authors\44.1khz\Vertical (44.1khz)"
    author_folder = r"E:\Dataset\All Authors\44.1khz\Vertical (44.1khz)"
    stoistica_folder = r"E:\Dataset\All STOISTICA Audio\Video Clips\Vertical\2s Added"
    book_folder = r"E:\Dataset\All Audiobook\Vertical"
    bg_music = r"E:\Dataset\ALL BG Music\58 mins Sub-Conscious Sleep Music 58 mins"
    output_folder = "output\Book Outputs"

    duration = 599  # Options: duration in seconds (e.g., 59, 119, 599, 30 * 60, 60 * 60, 23795 ,28799, 32948, 40270)
    iterations = 30  # Number of iterations to generate
    quality = "Extreme"  # Options: "Default", "High", "Higher", "Intense", "Extreme"
    bg_music_volume = 0  # Volume adjustment in decibels, 0 is default, negative values reduce volume
    final_audio_volume = 9  # in dB
    
    motivation_folder = r"E:\Dataset\All Motivation Clips\Fade-3db"
    altbg1_folder = r"E:\Dataset\All Video BG\Watermarked\Vertical\2 Minute\Stoic"#\Random\Exercise for subfolder only
    altbg2_folder = r"E:\Dataset\All Video BG\Watermarked\Vertical\Random" 
    altbg3_folder = r"E:\Dataset\All Video BG\Watermarked\Vertical\All Artwork"
    altbg4_folder = r"E:\Dataset\All Video BG\Watermarked\Vertical\Smoke"
    
    altbg_category = "Random"  # Replace with "Exercise", "Hiking", "Ocean", "God", "Monk", "Rock", "Time", "Stoic", "Random", or None
    #Only 10m videos can choose a category. If video is less than 599, it will always be randomized background.

    # New alternating folder logic, starting with altbg1, then altbg2, and altbg3
    altbg_folders = [altbg1_folder, altbg2_folder, altbg3_folder, altbg4_folder]
    altbg_index = 0  # Keeps track of which altbg to use next

    # Pass both altbg folders to alternate between them
    create_final_video_sequence(
        bg_folder, fg_folder, title_folder, author_folder, stoistica_folder,
        book_folder, motivation_folder, output_folder, duration, iterations, quality,
        bg_music, bg_music_volume, final_audio_volume,
        altbg1_folder, altbg2_folder, altbg3_folder, altbg4_folder
    )