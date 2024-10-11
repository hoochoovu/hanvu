import os
from moviepy.editor import VideoFileClip, ColorClip, concatenate_videoclips

def extend_videos_with_black_screen(input_folder, output_folder, extension_duration=3):
    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Process each .mp4 file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.mp4'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            
            # Load the original video
            video = VideoFileClip(input_path)
            
            # Create a black screen clip with no audio
            black_screen = ColorClip(size=video.size, color=(0, 0, 0), duration=extension_duration)
            black_screen = black_screen.set_audio(None)
            
            # Concatenate the original video with the black screen
            extended_video = concatenate_videoclips([video, black_screen])
            
            # Write the extended video to the output path using NVENC codec
            extended_video.write_videofile(output_path, codec='libx264', audio_codec='aac', ffmpeg_params=['-c:v', 'h264_nvenc'])
            
            # Close the clips
            video.close()
            black_screen.close()
            extended_video.close()
            
    print("Processing complete.")

# Example usage
input_folder = r'E:\Dataset\All STOISTICA Audio\Video Clips\Vertical\2s Added\New Authors Vertical\Bhagavad Gita'
output_folder = r'E:\Dataset\All STOISTICA Audio\Video Clips\Vertical\2s Added\New Authors Vertical\Bhagavad Gita\0.25 added'
extend_videos_with_black_screen(input_folder, output_folder)
