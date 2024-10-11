import os
from PIL import Image

# Resize scale for foreground image
SCALE_FACTOR = .2623

# Foreground overlay position
OFFSET_X = 1645
OFFSET_Y = 905

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

# Function to process and overlay images
def overlay_images(bg_folder, fg_folder, output_folder, output_format="jpg", fg_opacity=100):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    bg_images = [f for f in os.listdir(bg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    fg_images = [f for f in os.listdir(fg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

    for fg_file in fg_images:
        fg_image = Image.open(os.path.join(fg_folder, fg_file)).convert("RGBA")
        
        # Resize foreground image
        fg_width, fg_height = fg_image.size
        fg_image = fg_image.resize((int(fg_width * SCALE_FACTOR), int(fg_height * SCALE_FACTOR)), Image.LANCZOS)

        # Adjust the opacity of the foreground image
        fg_image = adjust_opacity(fg_image, fg_opacity)

        # Updated size after resizing
        fg_width, fg_height = fg_image.size
        
        # Create a subfolder inside the output folder for the foreground image
        fg_subfolder = os.path.join(output_folder, os.path.splitext(fg_file)[0])
        if not os.path.exists(fg_subfolder):
            os.makedirs(fg_subfolder)

        for bg_file in bg_images:
            bg_image = Image.open(os.path.join(bg_folder, bg_file)).convert("RGBA")
            bg_width, bg_height = bg_image.size

            # Check if the background image can fit the resized foreground with the offset
            if bg_width < fg_width + OFFSET_X or bg_height < fg_height + OFFSET_Y:
                print(f"Skipping {bg_file} with {fg_file}, background image too small for overlay.")
                continue

            # Create a copy of the background image to paste the foreground onto
            result_image = bg_image.copy()

            # Overlay the foreground image onto the background image
            result_image.paste(fg_image, (OFFSET_X, OFFSET_Y), fg_image)

            # Convert back to RGB and save the image
            result_image = result_image.convert("RGB")

            # Correct the output format for jpg
            if output_format.lower() == "jpg":
                output_format = "JPEG"
            
            # Save the image in the corresponding foreground subfolder
            output_file_name = f"[Mockup]{os.path.splitext(fg_file)[0]}_{bg_file}.{output_format.lower()}"
            output_path = os.path.join(fg_subfolder, output_file_name)
            result_image.save(output_path, format=output_format.upper())
            print(f"Saved: {output_path}")

# Main function
if __name__ == "__main__":
    bg_folder = r"E:\Python_Practice\Printify Mockup Image Combiner\Background Templates\2ndrun"
    fg_folder = "fg"
    output_folder = "output"
    
    # Choose output format, jpg or png
    output_format = "jpg"  # Can be 'png' or 'jpg'
    
    # Set foreground opacity (in percentage, 0 = fully transparent, 100 = fully opaque)
    fg_opacity = 100  # Example: 70% opacity

    overlay_images(bg_folder, fg_folder, output_folder, output_format, fg_opacity)
