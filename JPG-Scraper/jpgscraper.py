import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit

def scrape_jpgs(base_url, output_folder):
    # Ensure the output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Fetch the webpage content
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all .jpg links ending with "-585x1024" or "-1024x585"
    for img_tag in soup.find_all('img'):
        img_url = img_tag.get('src')
        if img_url and (img_url.endswith("-585x1024.jpg") or img_url.endswith("-1024x585.jpg")):
            # Modify the filename
            img_url_base = img_url.rsplit('-', 1)[0] + ".jpg"
            img_url_final = urljoin(base_url, img_url_base)
            filename = os.path.basename(urlsplit(img_url_base).path)

            # Download the image
            img_data = requests.get(img_url_final).content
            output_path = os.path.join(output_folder, filename)

            with open(output_path, 'wb') as f:
                f.write(img_data)

            print(f"Downloaded and saved {filename} to {output_folder}")

if __name__ == "__main__":
    # Set the URL of the page you want to scrape
    base_url = "https://wearthewisdom.com/ai-image-gen/"

    # Set the directory where you want to save the images
    output_folder = "downloaded_images"

    # Call the function to scrape images
    scrape_jpgs(base_url, output_folder)
