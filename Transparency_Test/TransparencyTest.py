import os
import subprocess

def process_videos(bg_folder, fg_folder, output_folder):
    """
    Processes videos using color keying method, ensuring output
    video ends with the foreground video's duration.

    Args:
        bg_folder: Path to the folder containing background videos.
        fg_folder: Path to the folder containing foreground videos.
        output_folder: Path to the folder where output videos will be saved.
    """

    for bg_file in os.listdir(bg_folder):
        if bg_file.endswith(".mp4"):
            bg_path = os.path.join(bg_folder, bg_file)

            for fg_file in os.listdir(fg_folder):
                if fg_file.endswith(".mp4"):
                    fg_path = os.path.join(fg_folder, fg_file)
                    output_file = os.path.join(output_folder, f"{os.path.splitext(fg_file)[0]}_output.mp4")

                    # Get foreground video duration using ffprobe
                    fg_duration_command = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", fg_path]
                    fg_duration_process = subprocess.run(fg_duration_command, capture_output=True, text=True)
                    fg_duration = float(fg_duration_process.stdout.strip())

                    # Color keying method (Corrected)
                    command = [
                        "ffmpeg", "-hwaccel", "cuda", "-i", bg_path, "-i", fg_path,
                        "-filter_complex", "[1]colorkey=0x000000:0.1:0.1[fg];[0][fg]overlay=0:0,trim=duration={:.2f}[out]".format(fg_duration),
                        "-map", "[out]", "-c:v", "libx264", "-preset", "veryfast", "-gpu", "0",
                        "-pix_fmt", "yuv420p", "-crf", "20",  "-y", output_file
                    ]
                    subprocess.run(command)

if __name__ == "__main__":
    bg_folder = "bg"
    fg_folder = "fg"
    output_folder = "output"

    # Process videos using color keying method
    process_videos(bg_folder, fg_folder, output_folder)