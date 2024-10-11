import os
from PIL import Image

# Parameters for each foreground image
fg_parameters = [
    {"scale": 0.0885, "offset_x": 160, "offset_y": 230, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 809, "offset_y": 230, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 1459, "offset_y": 230, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 2122, "offset_y": 230, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 2771, "offset_y": 230, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 3420, "offset_y": 230, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 160, "offset_y": 1181, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 809, "offset_y": 1181, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 1459, "offset_y": 1181, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 2122, "offset_y": 1181, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 2771, "offset_y": 1181, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 3420, "offset_y": 1181, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 160, "offset_y": 2199, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 809, "offset_y": 2199, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 1459, "offset_y": 2199, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 2122, "offset_y": 2199, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 2771, "offset_y": 2199, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 3420, "offset_y": 2199, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 160, "offset_y": 3151, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 809, "offset_y": 3151, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 1459, "offset_y": 3151, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 2122, "offset_y": 3151, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 2771, "offset_y": 3151, "crop_left": 0, "crop_right": 0},
    {"scale": 0.0885, "offset_x": 3420, "offset_y": 3151, "crop_left": 0, "crop_right": 0},
]

def adjust_opacity(image, opacity_percentage):
    if opacity_percentage < 0 or opacity_percentage > 100:
        raise ValueError("Opacity percentage must be between 0 and 100")
    alpha = image.split()[3]
    alpha_value = int(255 * (opacity_percentage / 100))
    alpha = alpha.point(lambda p: alpha_value)
    image.putalpha(alpha)
    return image

def crop_image(image, left, right):
    return image.crop((left, 0, right, image.height))

def overlay_images(bg_folder, fg_folder, output_folder, output_format="jpg", fg_opacity=100):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    bg_images = [f for f in os.listdir(bg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    fg_images = [f for f in os.listdir(fg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

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
            
            print(f"Processing {fg_file}...")
            fg_width, fg_height = fg_image.size
            fg_image = fg_image.resize((int(fg_width * scale), int(fg_height * scale)), Image.LANCZOS)
            
            resized_fg_width, resized_fg_height = fg_image.size
            cropped_fg_image = crop_image(fg_image, crop_left, resized_fg_width - crop_right)
            
            cropped_fg_image = adjust_opacity(cropped_fg_image, fg_opacity)
            
            result_image.paste(cropped_fg_image, (offset_x, offset_y), mask=cropped_fg_image)
        
        result_image = result_image.convert("RGB")
        
        if output_format.lower() == "jpg":
            output_format = "JPEG"
        
        output_file_name = f"[Mockup]_combined_{bg_file}.{output_format.lower()}"
        output_path = os.path.join(output_folder, output_file_name)
        result_image.save(output_path, format=output_format)
        print(f"Saved: {output_path}")

if __name__ == "__main__":
    bg_folder = r"bg"
    fg_folder = r"fg"
    output_folder = "output"
    output_format = "jpg"
    fg_opacity = 90

    overlay_images(bg_folder, fg_folder, output_folder, output_format, fg_opacity)