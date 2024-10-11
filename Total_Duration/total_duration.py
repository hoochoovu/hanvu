import os
import moviepy.editor as mpe

def get_media_duration(folder_path):
    total_duration = 0
    video_count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv',  # Add more video extensions if needed
                                       '.mp3', '.wav', '.ogg', '.aac')):  # Add more audio extensions if needed
                file_path = os.path.join(root, file)
                try:
                    video = mpe.VideoFileClip(file_path)
                    total_duration += video.duration
                    video_count += 1
                    video.close()
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    return total_duration, video_count

if __name__ == "__main__":
    folder_path = r"E:\Dataset\All Authors - 44.1khz\Test Horizontal (44.1khz)"
    total_duration, video_count = get_media_duration(folder_path)

    print(f"Total number of videos and audios: {video_count}")
    print(f"Total duration of all videos and audios combined: {total_duration} seconds")
    print(f"Total duration in minutes: {total_duration / 60}")
    print(f"Total duration in hours: {total_duration / 3600}")