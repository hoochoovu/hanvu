import os
from PIL import Image
import numpy as np
import cv2  # OpenCV is needed for perspective transform

# Resize scale for foreground image
SCALE_FACTOR = 1

# Cropping size (pixels) for foreground image
CROP_LEFT = 0
CROP_RIGHT = 0

# Function to adjust the opacity of an RGBA image using percentage
def adjust_opacity(image, opacity_percentage):
    if opacity_percentage < 0 or opacity_percentage > 100:
        raise ValueError("Opacity percentage must be between 0 and 100")

    alpha = image.split()[3]  # Extract the alpha channel
    alpha_value = int(255 * (opacity_percentage / 100))
    alpha = alpha.point(lambda p: alpha_value)  # Set alpha channel to the desired opacity
    image.putalpha(alpha)  # Put the modified alpha channel back
    return image

# Function to crop an image
def crop_image(image, left, right):
    return image.crop((left, 0, right, image.height))

# Function to apply perspective transform using OpenCV
def apply_perspective_transform(image, src_points, dst_points, output_size):
    # Convert the PIL image to a NumPy array (OpenCV format)
    image_array = np.array(image)

    # Compute the perspective transform matrix
    matrix = cv2.getPerspectiveTransform(np.float32(src_points), np.float32(dst_points))

    # Apply the perspective warp
    warped_image = cv2.warpPerspective(image_array, matrix, output_size)

    # Convert back to PIL image
    return Image.fromarray(warped_image)

# Function to process and overlay images
def overlay_images(bg_folder, fg_folder, output_folder, output_format="jpg", fg_opacity=100):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    bg_images = [f for f in os.listdir(bg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    fg_images = [f for f in os.listdir(fg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

    # Define the destination points (4 corners) for perspective transform
    # These can be adjusted for each foreground overlay as needed
    dst_top_left = (1505, 1150)
    dst_top_right = (2884, 1200)
    dst_bottom_right = (2782, 2400)
    dst_bottom_left = (1390, 2285)
    
    # Store the destination points in an array for easy access
    dst_points = [dst_top_left, dst_top_right, dst_bottom_right, dst_bottom_left]
    
    for fg_file in fg_images:
        fg_path = os.path.join(fg_folder, fg_file)
        fg_image = Image.open(fg_path).convert("RGBA")
        
        # Resize foreground image
        fg_width, fg_height = fg_image.size
        fg_image = fg_image.resize((int(fg_width * SCALE_FACTOR), int(fg_height * SCALE_FACTOR)), Image.LANCZOS)
        
        # Crop foreground image
        resized_fg_width, resized_fg_height = fg_image.size
        cropped_fg_image = crop_image(fg_image, CROP_LEFT, resized_fg_width - CROP_RIGHT)
        
        # Adjust the opacity of the foreground image
        cropped_fg_image = adjust_opacity(cropped_fg_image, fg_opacity)
        
        # Define source points for perspective transform (based on the current size of the cropped foreground image)
        src_points = [(0, 0), (cropped_fg_image.width, 0), (cropped_fg_image.width, cropped_fg_image.height), (0, cropped_fg_image.height)]
        
        for bg_file in bg_images:
            bg_path = os.path.join(bg_folder, bg_file)
            bg_image = Image.open(bg_path).convert("RGBA")
            bg_width, bg_height = bg_image.size

            # Apply perspective transform to the foreground image
            warped_fg_image = apply_perspective_transform(
                cropped_fg_image,
                src_points,
                dst_points,
                (bg_width, bg_height)  # Use background image dimensions for the output size
            )
            
            # Create a copy of the background image to paste the foreground onto
            result_image = bg_image.copy()

            # Paste the warped foreground image onto the background
            result_image.paste(warped_fg_image, (0, 0), mask=warped_fg_image)
            
            # Convert back to RGB and save the image
            result_image = result_image.convert("RGB")
            
            # Correct the output format for JPG
            if output_format.lower() == "jpg":
                output_format = "JPEG"
            
            # Save the image
            output_file_name = f"[Mockup]{os.path.splitext(fg_file)[0]}_{bg_file}.{output_format.lower()}"
            output_path = os.path.join(output_folder, output_file_name)
            result_image.save(output_path, format=output_format)
            print(f"Saved: {output_path}")

# Main function
if __name__ == "__main__":
    bg_folder = r"E:\Python_Practice\Printify Mockup Image Combiner\Perspective Mockup Generator\bg\h1"
    fg_folder = r"E:\Python_Practice\Printify Mockup Image Combiner\Perspective Mockup Generator\fg\5x4"
    output_folder = "output"
    
    # Choose output format, jpg or png
    output_format = "jpg"  # Can be 'png' or 'jpg'
    
    # Set foreground opacity (in percentage, 0 = fully transparent, 100 = fully opaque)
    fg_opacity = 90  # Example: 70% opacity

    overlay_images(bg_folder, fg_folder, output_folder, output_format, fg_opacity)
