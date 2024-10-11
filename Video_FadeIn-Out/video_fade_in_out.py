import os
import ffmpeg

def get_video_duration(video_path):
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe['streams'][0]['duration'])
        return duration
    except ffmpeg.Error as e:
        print(f"Error retrieving duration for {video_path}: {e}")
        return None

def apply_audio_fade_and_resample(video_path, output_path, volume_adjustment=-3, fade_in_duration=3, fade_out_duration=3, audio_sample_rate=44100):
    try:
        duration = get_video_duration(video_path)
        if duration is None:
            print(f"Skipping video: {video_path} due to missing duration.")
            return
        
        fade_out_start_time = max(0, duration - fade_out_duration)
        
        input_video = ffmpeg.input(video_path)
        
        # Apply volume adjustment
        audio = input_video.audio.filter('volume', volume=f'{volume_adjustment}dB')
        
        # Apply audio fades
        audio = audio.filter('afade', type='in', start_time=0, duration=fade_in_duration)
        audio = audio.filter('afade', type='out', start_time=fade_out_start_time, duration=fade_out_duration)
        
        # Resample audio
        audio = audio.filter('aresample', audio_sample_rate)
        
        # Combine processed audio with original video
        output = ffmpeg.output(input_video.video, audio, output_path,
                               vcodec='h264_nvenc',
                               acodec='aac',
                               video_bitrate='2M',
                               audio_bitrate='192k',
                               preset='fast')
        
        ffmpeg.run(output, overwrite_output=True)
        print(f"Processed video: {output_path}")
    except ffmpeg.Error as e:
        print(f"Error processing video {video_path}: {e}")

def process_videos(input_folder, output_folder, volume_adjustment=-3, fade_in_duration=3, fade_out_duration=3, audio_sample_rate=44100):
    for root, dirs, files in os.walk(input_folder):
        relative_path = os.path.relpath(root, input_folder)
        target_dir = os.path.join(output_folder, relative_path)
        os.makedirs(target_dir, exist_ok=True)
        
        for file in files:
            if file.endswith(('.mp4', '.mov', '.avi', '.mkv')):
                video_path = os.path.join(root, file)
                output_path = os.path.join(target_dir, file)
                apply_audio_fade_and_resample(video_path, output_path, volume_adjustment, fade_in_duration, fade_out_duration, audio_sample_rate)

if __name__ == '__main__':
    input_folder = r'E:\Dataset\All Motivation Clips'  # Change to your input folder
    output_folder = r'output'  # Change to your output folder
    volume_adjustment = -3  # Volume adjustment in decibels
    fade_in_duration = 3
    fade_out_duration = 3
    audio_sample_rate = 44100
    process_videos(input_folder, output_folder, volume_adjustment, fade_in_duration, fade_out_duration, audio_sample_rate)