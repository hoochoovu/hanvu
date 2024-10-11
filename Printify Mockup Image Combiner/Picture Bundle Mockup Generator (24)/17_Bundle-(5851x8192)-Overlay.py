import os
from PIL import Image
from natsort import natsorted

# Parameters for each foreground image
fg_parameters = [
    {"scale": 0.0821, "offset_x": 1021, "offset_y": 592, "crop_left": 0, "crop_right": 0},
    {"scale": 0.1080, "offset_x": 943, "offset_y": 1382, "crop_left": 0, "crop_right": 0},
    {"scale": 0.1669, "offset_x": 1655, "offset_y": 884, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0798, "offset_x": 2757, "offset_y": 850, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0814, "offset_x": 2737, "offset_y": 1600, "crop_left": 0, "crop_right": 0},
    {"scale": 0.2021, "offset_x": 3295, "offset_y": 941, "crop_left": 0, "crop_right": 0},
    {"scale": 0.2448, "offset_x": 4549, "offset_y": 592, "crop_left": 0, "crop_right": 0},
    {"scale": 0.2051, "offset_x": 6093, "offset_y": 364, "crop_left": 0, "crop_right": 0},
    {"scale": 0.1740, "offset_x": 917, "offset_y": 2396, "crop_left": 0, "crop_right": 0},
    {"scale": 0.2001, "offset_x": 2026, "offset_y": 2397, "crop_left": 0, "crop_right": 0},
    {"scale": 0.1046, "offset_x": 3470, "offset_y": 2862, "crop_left": 0, "crop_right": 0},
    {"scale": 0.1046, "offset_x": 4328, "offset_y": 2862, "crop_left": 0, "crop_right": 0},
    {"scale": 0.1587, "offset_x": 5040, "offset_y": 2862, "crop_left": 0, "crop_right": 0},
    {"scale": 0.1813, "offset_x": 6100, "offset_y": 2176, "crop_left": 0, "crop_right": 0},
    {"scale": 0.1031, "offset_x": 7273, "offset_y": 2171, "crop_left": 0, "crop_right": 0},
    {"scale": 0.1520, "offset_x": 703, "offset_y": 4002, "crop_left": 0, "crop_right": 0},
    {"scale": 0.2534, "offset_x": 7286, "offset_y": 3167, "crop_left": 0, "crop_right": 0},
]

def adjust_opacity(image, opacity_percentage):
    if opacity_percentage < 0 or opacity_percentage > 100:
        raise ValueError("Opacity percentage must be between 0 and 100")
    
    # Extract alpha channel and adjust its values
    alpha = image.split()[3]
    alpha_value = int(255 * (opacity_percentage / 100))
    
    # Set all non-transparent pixels to the new opacity and fully transparent for others
    alpha = alpha.point(lambda p: alpha_value if p > 0 else 0)
    image.putalpha(alpha)
    return image

def crop_image(image, left, right):
    return image.crop((left, 0, right, image.height))

def apply_final_overlay(base_image, overlay_image, opacity=100):
    """
    Apply a final overlay image to the base image, centering it.
    """
    base_width, base_height = base_image.size
    overlay_width, overlay_height = overlay_image.size
    
    # Calculate position to center the overlay
    x = (base_width - overlay_width) // 2
    y = (base_height - overlay_height) // 2
    
    print(f"Applying overlay: size={overlay_image.size}, position=({x}, {y})")
    
    overlay_image = adjust_opacity(overlay_image, opacity)
    
    # Create a new blank image with the same size as the base image
    result = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
    
    # Paste the base image
    result.paste(base_image, (0, 0))
    
    # Paste the overlay image
    result.paste(overlay_image, (x, y), overlay_image)
    
    return result

def overlay_images(bg_folder, fg_folder, overlay_folder, output_folder, output_format="jpg", fg_opacity=100, final_overlay_opacity=100):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    bg_images = natsorted([f for f in os.listdir(bg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))])
    fg_images = natsorted([f for f in os.listdir(fg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))])
    overlay_images_list = natsorted([f for f in os.listdir(overlay_folder) if f.lower().endswith(('png'))])

    if not overlay_images_list:
        raise ValueError("No overlay images found in the overlay folder.")

    # Ensure the overlay is in RGBA mode
    overlay_image = Image.open(os.path.join(overlay_folder, overlay_images_list[0])).convert("RGBA")
    print(f"Overlay image loaded: {overlay_image.size}, mode={overlay_image.mode}")

    for bg_file in bg_images:
        bg_path = os.path.join(bg_folder, bg_file)
        bg_image = Image.open(bg_path).convert("RGBA")
        result_image = bg_image.copy()

        for idx, fg_file in enumerate(fg_images):
            if idx >= len(fg_parameters):
                print(f"Warning: No parameters for {fg_file}. Skipping.")
                continue

            fg_path = os.path.join(fg_folder, fg_file)
            fg_image = Image.open(fg_path).convert("RGBA")
            
            fg_params = fg_parameters[idx]
            scale = fg_params["scale"]
            offset_x = fg_params["offset_x"]
            offset_y = fg_params["offset_y"]
            crop_left = fg_params["crop_left"]
            crop_right = fg_params["crop_right"]
            
            print(f"Processing {fg_file}... (scale={scale}, offset=({offset_x}, {offset_y}))")
            fg_width, fg_height = fg_image.size
            fg_image = fg_image.resize((int(fg_width * scale), int(fg_height * scale)), Image.LANCZOS)
            
            resized_fg_width, resized_fg_height = fg_image.size
            cropped_fg_image = crop_image(fg_image, crop_left, resized_fg_width - crop_right)
            
            cropped_fg_image = adjust_opacity(cropped_fg_image, fg_opacity)
            
            result_image.paste(cropped_fg_image, (offset_x, offset_y), mask=cropped_fg_image)
        
        # Apply final overlay
        result_image = apply_final_overlay(result_image, overlay_image, final_overlay_opacity)
        
        # Ensure correct format key for saving in JPEG format
        if output_format.lower() == "jpg":
            result_image = result_image.convert("RGB")  # For JPEG, no alpha channel
            output_format = "JPEG"  # Correct format for saving JPEG in PIL

        output_file_name = f"[Mockup]_combined_{bg_file}.{output_format.lower()}"
        output_path = os.path.join(output_folder, output_file_name)
        result_image.save(output_path, format=output_format.upper())  # Save the image
if __name__ == "__main__":
    bg_folder = r"bg17"
    fg_folder = r"fg17"
    overlay_folder = r"ol17"  # New folder for final overlay images
    output_folder = "output"
    output_format = "jpg"
    fg_opacity = 90
    final_overlay_opacity = 100  # Adjust this value as needed

    overlay_images(bg_folder, fg_folder, overlay_folder, output_folder, output_format, fg_opacity, final_overlay_opacity)
