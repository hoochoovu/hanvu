import os
import subprocess
import random

def get_video_files(folder):
    video_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                video_files.append(os.path.join(root, file))
    return video_files

def append_video_until_duration(fg_folder, output_path, target_duration):
    fg_files = get_video_files(fg_folder)
    current_duration = 0
    appended_list = []
    temp_output = "temp_appended.mp4"

    while current_duration < target_duration:
        if not fg_files:
            print("No more videos found in the foreground folder.")
            break

        video_path = random.choice(fg_files)
        if video_path not in appended_list:
            try:
                duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]).decode('utf-8').strip())

                if current_duration + duration <= target_duration:
                    if current_duration == 0:
                        subprocess.run(f"ffmpeg -i {video_path} {temp_output}", shell=True, check=True)
                    else:
                        # Use the concat demuxer for simpler concatenation
                        subprocess.run(f"ffmpeg -i {temp_output} -i {video_path} -filter_complex '[0:v][1:v]concat=n=2:v=1:a=0[v]' -map '[v]' -c:v libx264 -c:a copy {temp_output}", shell=True, check=True)
                    current_duration += duration
                    appended_list.append(video_path)
            except subprocess.CalledProcessError as e:
                print(f"Error processing video {video_path}: {e}")

    return temp_output

def append_audio(audio_list, output_path):
    temp_output = "temp_audio.mp3"
    if audio_list:
        first_audio = audio_list.pop(0)
        subprocess.run(f"ffmpeg -i {first_audio} {temp_output}", shell=True, check=True)

        for audio_path in audio_list:
            try:
                subprocess.run(f"ffmpeg -i {temp_output} -i {audio_path} -filter_complex '[0:a][1:a]concat=n=2:v=0:a=1[a]' -map '[a]' -c:a aac {temp_output}", shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error appending audio {audio_path}: {e}")

        subprocess.run(f"ffmpeg -i {temp_output} {output_path}", shell=True, check=True)

def apply_color_keying(video_path, output_path, color_key="black"):
    subprocess.run(f"ffmpeg -i {video_path} -vf 'chromakey=color={color_key}:similarity=0.1' {output_path}", shell=True, check=True)

def merge_videos(bg_video, fg_video, audio_path, output_path):
    subprocess.run(f"ffmpeg -i {bg_video} -i {fg_video} -i {audio_path} -filter_complex '[0:v][1:v]overlay=shortest=1[v]' -map '[v]' -map 2:a -c:v libx264 -crf 23 -preset medium -c:a aac {output_path}", shell=True, check=True)

def process_videos(bg_folder, fg_folder, output_folder, target_duration):
    os.makedirs(output_folder, exist_ok=True)
    appended_video = append_video_until_duration(fg_folder, os.path.join(output_folder, "appended_video.mp4"), target_duration)
    if not os.path.exists(appended_video):
        print(f"Failed to create appended video: {appended_video}")
        return

    bg_videos = get_video_files(bg_folder)
    if not bg_videos:
        print("No background videos found.")
        return

    bg_video = random.choice(bg_videos)

    # Extract audio from appended video
    audio_list = []
    subprocess.run(f"ffmpeg -i {appended_video} -vn -acodec copy {os.path.join(output_folder, 'temp_audio.mp3')}", shell=True, check=True)
    audio_list.append(os.path.join(output_folder, 'temp_audio.mp3'))

    # Apply color keying
    color_keyed_video = os.path.join(output_folder, "color_keyed_video.mp4")
    apply_color_keying(appended_video, color_keyed_video)

    # Merge videos and audio
    merge_videos(bg_video, color_keyed_video, os.path.join(output_folder, 'final_output.mp4'), os.path.join(output_folder, 'final_output.mp4'))
    print(f"Final output saved to: {os.path.join(output_folder, 'final_output.mp4')}")

if __name__ == "__main__":
    bg_folder = "bg"
    fg_folder = "fg"
    output_folder = "output"
    target_duration = 300  # 5 minutes

    process_videos(bg_folder, fg_folder, output_folder, target_duration)