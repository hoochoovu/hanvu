import os
from PIL import Image

# Resize scale for foreground image
SCALE_FACTOR = .2475

# Foreground overlay position
OFFSET_X = 980 #Higher number moves left, Lower Number moves right
OFFSET_Y = 1230 #Higher number moves down, Lower Number moves up

# Cropping size (pixels) for foreground image
CROP_LEFT = 10
CROP_RIGHT = 10

# Function to adjust the opacity of an RGBA image using percentage
def adjust_opacity(image, opacity_percentage):
    if opacity_percentage < 0 or opacity_percentage > 100:
        raise ValueError("Opacity percentage must be between 0 and 100")

    alpha = image.split()[3]  # Extract the alpha channel
    # Convert percentage to alpha value (0-255)
    alpha_value = int(255 * (opacity_percentage / 100))
    alpha = alpha.point(lambda p: alpha_value)  # Set alpha channel to the desired opacity
    image.putalpha(alpha)  # Put the modified alpha channel back
    return image

# Function to crop an image
def crop_image(image, left, right):
    return image.crop((left, 0, right, image.height))

# Function to process and overlay images
def overlay_images(bg_folder, fg_folder, output_folder, output_format="jpg", fg_opacity=100):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    bg_images = [f for f in os.listdir(bg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    fg_images = [f for f in os.listdir(fg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

    for fg_file in fg_images:
        fg_path = os.path.join(fg_folder, fg_file)
        fg_image = Image.open(fg_path).convert("RGBA")
        
        # Resize foreground image
        print(f"Resizing {fg_file}...")
        fg_width, fg_height = fg_image.size
        fg_image = fg_image.resize((int(fg_width * SCALE_FACTOR), int(fg_height * SCALE_FACTOR)), Image.LANCZOS)
        
        print(f"Original size: {fg_width}x{fg_height}")
        print(f"Resized size: {fg_image.size}")
        
        # Crop foreground image (29 pixels from left and right)
        resized_fg_width, resized_fg_height = fg_image.size
        cropped_fg_image = crop_image(fg_image, CROP_LEFT, resized_fg_width - CROP_RIGHT)
        
        print(f"Cropped size: {cropped_fg_image.size}")
        
        # Adjust the opacity of the foreground image
        print(f"Adjusting opacity of {fg_file}...")
        cropped_fg_image = adjust_opacity(cropped_fg_image, fg_opacity)
        
        print(f"Opacity: {fg_opacity}")
        
        # Create a subfolder inside the output folder for the foreground image
        fg_subfolder = os.path.join(output_folder, os.path.splitext(fg_file)[0])
        if not os.path.exists(fg_subfolder):
            os.makedirs(fg_subfolder)
        
        for bg_file in bg_images:
            bg_path = os.path.join(bg_folder, bg_file)
            bg_image = Image.open(bg_path).convert("RGBA")
            bg_width, bg_height = bg_image.size
            
            # Check if the background image can fit the resized foreground with the offset
            if bg_width < cropped_fg_image.width + OFFSET_X or bg_height < cropped_fg_image.height + OFFSET_Y:
                print(f"Skipping {bg_file} with {fg_file}, background image too small for overlay.")
                continue
            
            # Create a copy of the background image to paste the foreground onto
            result_image = bg_image.copy()
            
            # Adjust the position calculation
            position_x = bg_width - cropped_fg_image.width - OFFSET_X
            position_y = OFFSET_Y

            # Ensure position_x is not negative
            if position_x < 0:
                print(f"Foreground image {fg_file} is too wide to fit on the background {bg_file}.")
                continue

            # Paste the foreground image onto the background at the correct position
            print(f"Pasting {fg_file} onto {bg_file}...")
            result_image.paste(cropped_fg_image, (position_x, position_y), mask=cropped_fg_image)
            
            # Convert back to RGB and save the image
            result_image = result_image.convert("RGB")
            
            # Correct the output format for JPG
            if output_format.lower() == "jpg":
                output_format = "JPEG"
            
            # Save the image in the corresponding foreground subfolder
            output_file_name = f"[Mockup]{os.path.splitext(fg_file)[0]}_{bg_file}.{output_format.lower()}"
            output_path = os.path.join(fg_subfolder, output_file_name)
            result_image.save(output_path, format=output_format)
            print(f"Saved: {output_path}")

# Main function
if __name__ == "__main__":
    bg_folder = r"E:\Python_Practice\Printify Mockup Image Combiner\Background Templates\Canva\1-Canva"
    fg_folder = r"E:\Python_Practice\Printify Mockup Image Combiner\Canva Mockup Generator\canva_fg\2x3"
    output_folder = "output"
    
    # Choose output format, jpg or png
    output_format = "jpg"  # Can be 'png' or 'jpg'
    
    # Set foreground opacity (in percentage, 0 = fully transparent, 100 = fully opaque)
    fg_opacity = 90  # Example: 70% opacity

    overlay_images(bg_folder, fg_folder, output_folder, output_format, fg_opacity)
