import os
import cv2

def process_video(video_path, output_folder, frame_interval=36, max_photos=4):
    # Create a VideoCapture object
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return

    frame_count = 0
    photo_count = 0
    success = True

    while success and photo_count < max_photos:
        success, frame = cap.read()
        if not success:
            break

        # Save every 36th frame as a .jpg image
        if frame_count % frame_interval == 0:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            frame_filename = os.path.join(output_folder, f"{video_name}_frame_{frame_count}.jpg")
            cv2.imwrite(frame_filename, frame)
            photo_count += 1
        
        frame_count += 1

    # Release the VideoCapture object
    cap.release()

def process_folder(input_folder, output_folder, frame_interval=36, max_photos=4):
    for root, dirs, files in os.walk(input_folder):
        # Determine the relative path to maintain folder structure
        relative_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, relative_path)
        os.makedirs(output_subfolder, exist_ok=True)

        for file in files:
            if file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                video_path = os.path.join(root, file)
                process_video(video_path, output_subfolder, frame_interval, max_photos)

if __name__ == "__main__":
    input_folder = r"E:\Dataset\All Video BG\Non-Watermarked\Vertical\1 Minute"
    output_folder = r"E:\Dataset\All Video BG\Non-Watermarked\Vertical\1 Minute\VIDEO_STILLS"
    
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    process_folder(input_folder, output_folder)