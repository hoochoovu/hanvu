import os
import subprocess
import random
import datetime

# Set the GPU ID to use
gpu_id = 0
os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

# Global variable to track used videos from input folder 2
used_videos_2 = []

def get_file_duration(file_path):
    """Gets the duration of a video file using ffprobe."""
    command = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path
    ]
    try:
        output = subprocess.check_output(command).decode('utf-8').strip()
        return float(output)
    except subprocess.CalledProcessError:
        print(f"Error getting file duration for {file_path}.")
        return None

def add_fade_effect(video1, video2, output_file, prepend, transition_duration, codec):
    """Applies fade transitions while appending or prepending videos."""
    # Determine which video comes first
    if prepend:
        first_video, second_video = video2, video1
    else:
        first_video, second_video = video1, video2

    # Get durations
    duration1 = get_file_duration(first_video)
    duration2 = get_file_duration(second_video)
    if duration1 is None or duration2 is None:
        print("Could not retrieve video durations. Skipping.")
        return False

    # Calculate the offset for the fade transition
    offset = duration1 - transition_duration

    # Construct the ffmpeg filter_complex with settb and fps to match timebases and frame rates
    filter_complex = (
        f"[0:v]fps=30,format=pix_fmts=yuv420p,settb=1/30,setpts=PTS-STARTPTS[v0];"
        f"[1:v]fps=30,format=pix_fmts=yuv420p,settb=1/30,setpts=PTS-STARTPTS+{offset}/TB[v1];"
        f"[v0][v1]xfade=transition=fade:duration={transition_duration}:offset={offset}[v];"
        f"[0:a]asettb=1/48000,asetpts=PTS-STARTPTS[a0];"
        f"[1:a]asettb=1/48000,asetpts=PTS-STARTPTS+{offset}/TB[a1];"
        f"[a0][a1]acrossfade=d={transition_duration}[a]"
    )

    command = [
        'ffmpeg', '-i', first_video, '-i', second_video,
        '-filter_complex', filter_complex,
        '-map', '[v]', '-map', '[a]',
        '-c:v', codec, '-c:a', 'aac', output_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Video merged and saved to {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to merge videos: {e}")
        return False

def extract_first_six_words(filename):
    """Extracts the first six real words from a filename."""
    words = ''.join(c if c.isalpha() else ' ' for c in os.path.splitext(filename)[0]).split()
    return '_'.join(words[:6])

def random_select_video(videos):
    """Selects a video randomly from a list without repeats until all videos have been used."""
    global used_videos_2
    if len(used_videos_2) >= len(videos):
        used_videos_2 = []  # Reset the list if all videos have been used
    available_videos = [v for v in videos if v not in used_videos_2]
    selected_video = random.choice(available_videos)
    used_videos_2.append(selected_video)
    return selected_video

def insert_video_metadata(file_path, title, artist, genre, copyright, description):
    """Inserts metadata into the video file."""
    temp_file = file_path + ".temp.mp4"
    command = [
        'ffmpeg', '-y', '-i', file_path, '-c', 'copy',
        '-metadata', f"title={title}",
        '-metadata', f"artist={artist}",
        '-metadata', f"genre={genre}",
        '-metadata', f"copyright={copyright}",
        '-metadata', f"description={description}",
        temp_file
    ]
    try:
        subprocess.run(command, check=True)
        os.replace(temp_file, file_path)  # Overwrite original file
        print(f"Metadata added to {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to insert metadata: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    input_folder_1 = r"E:\Python_Practice\Video_Podcast_Maker\podcast_maker_output"
    input_folder_2 = r"E:\Python_Practice\Video_Music_Maker\music_maker_output"
    output_folder = "Output_Combined"
    transition_duration = 3  # Duration of the fade effect in seconds
    codec = 'h264_nvenc'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    videos_1 = [
        os.path.join(input_folder_1, f)
        for f in os.listdir(input_folder_1) if f.endswith(('.mp4', '.mov'))
    ]
    videos_2 = [
        os.path.join(input_folder_2, f)
        for f in os.listdir(input_folder_2) if f.endswith(('.mp4', '.mov'))
    ]

    for video1 in videos_1:
        video2 = random_select_video(videos_2)
        prepend = random.choice([True, False])

        video1_name = extract_first_six_words(os.path.basename(video1))
        video2_name = extract_first_six_words(os.path.basename(video2))
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file_name = f"[music+pod]{video1_name}_and_{video2_name}_{timestamp}.mp4"
        output_file = os.path.join(output_folder, output_file_name)

        success = add_fade_effect(
            video1, video2, output_file, prepend, transition_duration, codec
        )

        if success:
            insert_video_metadata(
                output_file,
                title="Stoic Radio - Stoistica - Stoicism Podcast",
                artist="Stoic Radio - Stoistica",
                genre="Motivational",
                copyright="Stoic Radio - Stoistica 2024",
                description="A motivational video about stoicism."
            )

if __name__ == "__main__":
    main()
