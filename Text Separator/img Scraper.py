import requests
from bs4 import BeautifulSoup
import os

def scrape_images(url, output_folder):
    """
    Scrapes a webpage for any image files and saves them to a specified folder.

    Args:
        url (str): The URL of the webpage to scrape.
        output_folder (str): The path to the folder where images will be saved.
    """

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Fetch the webpage content
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all image elements (no specific extension check)
    images = soup.find_all('img', src=True)  

    # Initialize counter
    image_count = 0

    # Iterate through the images and download them
    for i, image in enumerate(images):
        image_url = image['src']
        image_name = f"image_{i}.{os.path.splitext(image_url)[1][1:]}"  # Get extension
        image_path = os.path.join(output_folder, image_name)

        try:
            # Download the image
            image_data = requests.get(image_url).content
            with open(image_path, 'wb') as f:
                f.write(image_data)
            print(f"Downloaded: {image_name}")
            image_count += 1  # Increment counter
        except Exception as e:
            print(f"Error downloading {image_url}: {e}")

    print(f"Total images found and downloaded: {image_count}")

if __name__ == "__main__":
    url = "https://fybre.us/"  # Replace with the actual URL
    output_folder = r"E:\Dataset\BYLT (do not delete)\FYBRE\Images"  # Replace with your desired folder name

    scrape_images(url, output_folder)
    print("Scraping completed!")