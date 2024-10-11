import replicate
import time
import os
import requests
from PIL import Image
from io import BytesIO
import hashlib
import datetime
import re  # Import regex to clean filenames

# Set your Replicate API token as an environment variable or directly here
os.environ["REPLICATE_API_TOKEN"] = "id_key"

# Set the output folder for images
output_folder = "output_images_2ndrun"
os.makedirs(output_folder, exist_ok=True)

# Function to clean the filename by removing or replacing illegal characters
def clean_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Function to download the image and save it
def save_image(url, output_folder, prompt, image_format, output_quality):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    
    # Generate file name based on the first 6 words of the prompt and a timestamp
    first_words = '_'.join(prompt.split()[:6])
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Clean up the first words to remove illegal characters
    first_words = clean_filename(first_words)
    
    # Set file extension based on the desired output format
    file_extension = image_format.lower()
    file_name = f'{first_words}_{timestamp}.{file_extension}'
    
    file_path = os.path.join(output_folder, file_name)
    
    # Save with specified quality if not a PNG
    if file_extension == 'png':
        img.save(file_path)
    else:
        img.save(file_path, quality=output_quality)
    
    return file_path

# Function to get the hash of the image content
def get_image_hash(image_url):
    response = requests.get(image_url)
    return hashlib.md5(response.content).hexdigest()

# Main program logic
def generate_image(prompt, model_name="black-forest-labs/flux-1.1-pro", max_iterations=10, wait_time=15, seed=None, width=512, height=512, aspect_ratio="1:1", image_format="webp", output_quality=80, safety_tolerance=2, prompt_upsampling=True):
    
    previous_hash = None
    same_image_count = 0

    # Prepare the input for the API with new parameters
    input_data = {
        "prompt": prompt,
        "prompt_upsampling": prompt_upsampling,
        "seed": seed,
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio,
        "output_format": image_format,
        "output_quality": output_quality,
        "safety_tolerance": safety_tolerance,
    }

    for i in range(max_iterations):
        # Run the prediction
        prediction = replicate.predictions.create(model=model_name, input=input_data)
        
        # Poll for the image result
        while prediction.status not in ["succeeded", "failed"]:
            print(f"Prediction status: {prediction.status}. Waiting for completion...")
            time.sleep(wait_time)
            prediction.reload()

        if prediction.status == "succeeded":
            # Debug output to inspect what the API returns
            print(f"Prediction output: {prediction.output}")

            # Try to get the image URL from the prediction output
            try:
                image_url = prediction.output  # Removed [0] since output itself is the URL
                if not image_url.startswith('http'):
                    raise ValueError(f"Invalid image URL: {image_url}")
            except Exception as e:
                print(f"Error fetching image URL: {e}")
                break

            # Get image hash to detect if the image is a duplicate
            current_hash = get_image_hash(image_url)

            # Compare hash to check if the image is the same as the last one
            if current_hash == previous_hash:
                same_image_count += 1
                print(f"Same image detected {same_image_count} times in a row.")
            else:
                same_image_count = 0  # Reset the count if the image is different
                previous_hash = current_hash

            # Save the image
            image_path = save_image(image_url, output_folder, prompt, image_format, output_quality)
            print(f"Saved new image to {image_path}")

            # Stop if the image is the same 3 times in a row
            if same_image_count >= 3:
                print("Image has not changed for 3 consecutive checks. Stopping.")
                break
        else:
            print(f"Prediction failed. Status: {prediction.status}")
            break

        # Wait before checking the next prediction
        time.sleep(wait_time)

if __name__ == "__main__":
    # Example prompt with new adjustable parameters
    prompt = """in the style of leonid afremov:1.3, afremovian, a silhouette image:1.3, closeup, portrait, dark with contrast, glowing highlights, colorful, peaceful, beautiful scene, perfect eyes, Marcus Aurelius wearing a white roman toga as a stoic greek philosopher, interior of dimly lit an ancient temple background, he is calm, brush strokes, (Marcus Aurelius:1.3), he is focused in concentration, detailed, intricate details, realistic, dramatic and intense, epic, thinking in deep thought, leonid afremov, post-impressionism, impressionism, abstract expressionism, cubism, pointillism, gouache"""
    
    # You can adjust these settings to control the output
    wait_time = 15
    max_iterations = 25
    seed = -1  # Example seed for reproducibility
    width = 1344
    height = 1344
    aspect_ratio = "custom"  # Change to "custom" to use width and height
    image_format = "jpg"  # Choose between "webp", "jpg", or "png"
    output_quality = 100  # Only relevant for jpg and webp
    safety_tolerance = 5  # From 1 (strict) to 5 (permissive)
    prompt_upsampling = True  # Enable prompt upsampling for more creativity

    generate_image(
        prompt,
        wait_time=wait_time,
        max_iterations=max_iterations,
        seed=seed,
        width=width,
        height=height,
        aspect_ratio=aspect_ratio,
        image_format=image_format,
        output_quality=output_quality,
        safety_tolerance=safety_tolerance,
        prompt_upsampling=prompt_upsampling,
    )
