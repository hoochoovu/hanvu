import os
import random
import subprocess
from datetime import datetime
import logging
import re  # Import re module

# Setup logging configuration
logging.basicConfig(filename='video_processing.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set GPU ID
gpu_id = 1  # Change this to select a different GPU (0, 1, etc.)
os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

QUALITY_SETTINGS = {
    "Default": "2000k",
    "High": "4000k",
    "Higher": "6000k",
    "Intense": "8000k",
    "Extreme": "10000k"
}

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

def sanitize_filename(filename):
    """Removes invalid characters from a filename."""
    invalid_chars = '<>:"/\\|?*'
    return ''.join(c for c in filename if c not in invalid_chars)

def get_video_info(video_path):
    """Retrieve video width and height using ffprobe."""
    info = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=s=x:p=0", video_path
        ],
        capture_output=True,
        text=True
    ).stdout.strip().split('x')
    return int(info[0]), int(info[1])

def get_video_duration(video_path):
    """Retrieve video duration using ffprobe."""
    duration = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ],
        capture_output=True,
        text=True
    ).stdout.strip()
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
              for file in files if file.endswith((".mp4", ".avi", ".mov", ".mkv")) and os.path.join(root, file) not in used_videos]

    if not videos:
        raise FileNotFoundError(f"No more unused videos found in {folder}. All videos have been used.")

    selected_video = random.choice(videos)
    used_videos.add(selected_video)
    return selected_video

def ensure_unique_bg_videos(altbg_folders, used_bg_videos, required_duration):
    """Select background videos without duplication to meet or exceed the required duration."""
    total_bg_duration = 0
    bg_videos = []

    while total_bg_duration < required_duration:
        selected_folder = random.choice(altbg_folders)
        try:
            next_bg_video = select_random_video_without_reuse(selected_folder, used_bg_videos)
            bg_videos.append(next_bg_video)
            total_bg_duration += get_video_duration(next_bg_video)
        except FileNotFoundError:
            logging.warning(f"All videos in {selected_folder} have been used once. Resetting used videos for this folder.")
            # Clear used videos for this folder
            folder_videos = {v for v in used_bg_videos if v.startswith(selected_folder)}
            used_bg_videos -= folder_videos
            continue

    return bg_videos

def merge_videos(bg_concat_path, fg_path, output_video_path, crop_top=0, crop_bottom=0, transparency_color='none', alpha=1.0, quality="Default", position='center'):
    """Merges background and foreground videos with specified transparency, cropping, and position."""
    logging.info(f"Merging videos with foreground: {fg_path} and background: {bg_concat_path}")
    
    try:
        fg_width, fg_height = get_video_info(fg_path)
        bg_width, bg_height = get_video_info(bg_concat_path)
    
        # Crop the FG video if needed
        crop_filter = ''
        if crop_top > 0 or crop_bottom > 0:
            crop_height = fg_height - crop_top - crop_bottom
            crop_filter = f"crop=w=in_w:h={crop_height}:x=0:y={crop_top},"
            logging.info(f"Applying crop to FG video: top={crop_top}, bottom={crop_bottom}")
        else:
            crop_height = fg_height  # No cropping
    
        # Adjust offsets based on position
        scaled_fg_width = fg_width  # Assuming no scaling
        scaled_fg_height = crop_height  # After cropping
    
        x_offset = (bg_width - scaled_fg_width) // 2  # Center horizontally by default
    
        if position == 'center':
            y_offset = (bg_height - scaled_fg_height) // 2
        elif position == 'top':
            y_offset = 0
        elif position == 'bottom':
            y_offset = bg_height - scaled_fg_height
        elif position == 'custom':
            # You can set custom x_offset and y_offset if needed
            y_offset = (bg_height - scaled_fg_height) // 2  # Default to center vertically
            # Adjust x_offset and y_offset as per your requirements
        else:
            # Default to center if position is unrecognized
            y_offset = (bg_height - scaled_fg_height) // 2
            logging.warning(f"Unrecognized position '{position}', defaulting to center.")
    
        bitrate = QUALITY_SETTINGS.get(quality, "2000k")  # Default to "2000k" if quality not found
    
        # Build the filter complex
        # Apply colorkey if transparency_color is set
        transparency_filter = ''
        if transparency_color.lower() == 'black':
            transparency_filter = 'colorkey=black:0.1:0.1,'
        elif transparency_color.lower() == 'white':
            transparency_filter = 'colorkey=white:0.1:0.1,'
    
        # Apply alpha if not 1.0
        alpha_filter = ''
        if alpha < 1.0:
            alpha_filter = f"format=rgba,colorchannelmixer=aa={alpha},"
    
        # Build the full filter chain
        fg_filter = f"{crop_filter}{transparency_filter}{alpha_filter}scale={scaled_fg_width}:{scaled_fg_height}[fg];"
        overlay_filter = f"[0:v][fg]overlay=x={x_offset}:y={y_offset}[video]"
    
        filter_complex = f"[1:v]{fg_filter}{overlay_filter}"
    
        # Build ffmpeg command for video merging
        command = [
            "ffmpeg", "-hwaccel", "cuda", "-i", bg_concat_path, "-i", fg_path,
            "-filter_complex", filter_complex,
            "-map", "[video]", "-map", "1:a?",  # Include the audio from the foreground video if it exists
            "-c:v", "h264_nvenc", "-preset", "slow", "-b:v", bitrate, "-c:a", "aac", "-b:a", "192k",
            "-y", output_video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        logging.info(f"FFmpeg output:\n{result.stdout}")
        if result.stderr:
            logging.error(f"FFmpeg errors:\n{result.stderr}")
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
    except Exception as e:
        logging.error(f"Error during video merging: {e}")
        raise


def select_random_audio(folder, used_audios):
    """Selects a random audio file from a folder, including subfolders."""
    audios = [os.path.join(root, f)
              for root, _, files in os.walk(folder)
              for f in files
              if f.lower().endswith(('.mp3', '.wav')) and os.path.join(root, f) not in used_audios]
    if not audios:
        raise FileNotFoundError(f"No unused audio files found in {folder}.")
    selected_audio = random.choice(audios)
    used_audios.add(selected_audio)
    return selected_audio

def merge_audio_to_video(video_path, bg_music=None, bg_music_volume=0, final_audio_volume=0, used_audios=set()):
    """Merges background music into a video if bg_music is provided."""
    logging.info(f"Merging audio to video: {video_path} with background music: {bg_music}")

    video_duration = get_video_duration(video_path)

    if bg_music is None:
        # No background music, adjust final audio volume if needed
        if final_audio_volume != 0:
            # Adjust audio volume
            output_video_path = f"{os.path.splitext(video_path)[0]}_adjusted_audio.mp4"
            command = [
                "ffmpeg", "-hwaccel", "cuda", "-i", video_path,
                "-filter:a", f"volume={final_audio_volume}dB",
                "-c:v", "copy", "-y", output_video_path
            ]
            subprocess.run(command, check=True)
            return output_video_path, ''
        else:
            # No adjustments needed
            return video_path, ''
    else:
        if os.path.isdir(bg_music):
            bg_music_path = select_random_audio(bg_music, used_audios)
        else:
            bg_music_path = bg_music

        # Ensure the bg_music_path exists
        if not os.path.exists(bg_music_path):
            raise FileNotFoundError(f"Background music file not found: {bg_music_path}")

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

def create_final_video_sequence(fg_folder, altbg_folders, output_folder, iterations, quality, bg_music=None, bg_music_volume=0, final_audio_volume=0, crop_top=0, crop_bottom=0, transparency_color='none', alpha=1.0, position='center'):
    """Creates the final video sequence based on the new requirements."""
    os.makedirs(output_folder, exist_ok=True)

    used_fg_videos = set()
    used_bg_videos = set()
    used_audios = set()

    fg_videos = [os.path.join(root, file)
                 for root, _, files in os.walk(fg_folder)
                 for file in files if file.endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    if not fg_videos:
        raise FileNotFoundError(f"No videos found in fg_folder: {fg_folder}")

    for i in range(iterations):
        try:
            logging.info(f"Starting iteration {i+1} of {iterations}")

            if len(used_fg_videos) == len(fg_videos):
                logging.info("All foreground videos have been used. Resetting used_fg_videos.")
                used_fg_videos.clear()

            # Select an fg music video, avoiding duplicates
            while True:
                fg_video = random.choice(fg_videos)
                if fg_video not in used_fg_videos:
                    used_fg_videos.add(fg_video)
                    break

            fg_duration = get_video_duration(fg_video)

            # Build the background video
            bg_videos = ensure_unique_bg_videos(altbg_folders, used_bg_videos, fg_duration)

            # Concatenate bg videos
            with open("bg_concat_list.txt", "w") as f:
                for bg_path in bg_videos:
                    f.write(f"file '{bg_path}'\n")

            bg_concat_path = "concatenated_bg.mp4"
            command = [
                "ffmpeg", "-hwaccel", "cuda", "-f", "concat", "-safe", "0", "-i", "bg_concat_list.txt",
                "-c:v", "copy", "-y", bg_concat_path
            ]
            subprocess.run(command, check=True)

            # Trim bg video to match fg duration
            trimmed_bg_path = "trimmed_bg.mp4"
            trim_video_to_duration(bg_concat_path, trimmed_bg_path, fg_duration)

            # Overlay fg video onto bg video
            final_output_path = os.path.join(output_folder, f"final_output_{i+1}.mp4")
            merge_videos(trimmed_bg_path, fg_video, final_output_path, crop_top, crop_bottom, transparency_color, alpha, quality=quality, position=position)

            # Merge audio if bg_music is provided
            output_video_with_audio, first_two_words = merge_audio_to_video(final_output_path, bg_music, bg_music_volume, final_audio_volume, used_audios)

            # **Extract FG video filename part for naming**
            fg_filename = os.path.splitext(os.path.basename(fg_video))[0]
            fg_filename = sanitize_filename(fg_filename)
            words = re.split(r'[\s_-]+', fg_filename)
            first_six_words = words[:6]
            fg_name_part = '_'.join(first_six_words)

            # Add timestamp to final file name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_name = os.path.join(
                output_folder,
                f"Stoic Radio_Music_Video_{fg_name_part}_{timestamp}_{i+1}.mp4"
            )
            os.rename(output_video_with_audio, final_name)

            # Insert metadata
            insert_video_metadata(
                final_name,
                title="Stoic Radio Stoistica Stoicism Podcast",  # Replace with your desired title
                artist="Stoistica Stoic Radio",  # Replace with artist name
                genre="Motivational",  # Replace with the appropriate genre
                copyright="Stoistica 2024",  # Replace with your copyright information
                description="Stoic Radio. A motivational video about stoicism.",  # Replace with your video description
            )

            # Cleanup
            try_remove_file(bg_concat_path)
            try_remove_file(trimmed_bg_path)
            try_remove_file(final_output_path)
            try_remove_file("bg_concat_list.txt")

            logging.info(f"Final video created: {final_name}")
            print(f"Final video created: {final_name}")

        except Exception as e:
            logging.error(f"Error during iteration {i+1}: {e}")
            print(f"Error during iteration {i+1}: {e}")
            
if __name__ == "__main__": 
    
    # Input folders
    fg_folder = r"E:\Dataset\All Notebook Audio\Ready Video Clips White Square"
    altbg1_folder = r"E:\Dataset\All Music Video BG Videos"
    altbg2_folder = r"E:\Dataset\All Music Video BG Videos\Gladiator 3s"
    altbg3_folder = r"E:\Dataset\All Music Video BG Videos\All Artwork 3s"
    altbg4_folder = r"E:\Dataset\All Music Video BG Videos\All Pexel-Pixabay 3s"
    altbg5_folder = r"E:\Dataset\All Music Video BG Videos\All Stoic 3s"
    #altbg6_folder = r""
    # Add more altbg folders as needed

    altbg_folders = [altbg1_folder, altbg2_folder, altbg3_folder, altbg4_folder, altbg5_folder]

    output_folder = "music_maker_output"

    iterations = 57  # Number of videos to create
    quality = "Extreme"  # Options: "Default", "High", "Higher", "Intense", "Extreme"

    bg_music = None  # Set to path of bg music or None to not use bg music
    bg_music_volume = 0  # Volume adjustment in decibels, negative values reduce volume
    final_audio_volume = 9  # in dB

    crop_top = 1080  # Number of pixels to crop from top of FG video
    crop_bottom = 0  # Number of pixels to crop from bottom of FG video
    transparency_color = 'black'  # Options: 'black', 'white', 'none'
    alpha = 1  # Alpha transparency of FG video, between 0.0 (fully transparent) and 1.0 (fully opaque)

    position = 'bottom'  # Options: 'center', 'top', 'bottom', 'custom'

    create_final_video_sequence(
        fg_folder, altbg_folders, output_folder, iterations, quality,
        bg_music, bg_music_volume, final_audio_volume,
        crop_top, crop_bottom, transparency_color, alpha,
        position
    )