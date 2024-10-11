import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def scrape_and_format_links(url, filename="links.txt", folder="output"):
    """
    Scrapes video links from a given URL, formats them, and saves them to a text file.
    """
    # Create output folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)

    # Create a file to store the links
    filepath = os.path.join(folder, filename)
    with open(filepath, "w") as f:
        # Initialize browser
        driver = webdriver.Chrome()  # Assuming you have ChromeDriver installed
        driver.get(url)

        # Load the page fully
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "main-content")))

        # Loop through the page and extract links
        links_found = 0
        while links_found < 100:
            try:
                # Get the main content
                main_content = driver.find_element(By.ID, "main-content")

                # Find all links
                links = main_content.find_elements(By.CSS_SELECTOR, "a[data-testid='next-link']")

                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        # Check if the href starts with the expected pattern
                        if href.startswith("https://www.pexels.com/video"): 
                            # Print the original href
                            print(f"Original href: {href}") 

                            # Extract the video ID 
                            #split_id = href.split("/")[-2]
                            video_id = href.split("/")[-2].split("-")[-1]

                            # Construct the new link format
                            new_link = f"https://www.pexels.com/download/video/{video_id}"

                            # Print the link
                            print(f"Extracted Link: {new_link}")

                            # Write the link to the file
                            f.write(new_link + "\n")
                            links_found += 1

                            # Stop when 100 links are found
                            if links_found >= 100:
                                break
                        else:
                            print(f"Skipping link: {href} - Does not match expected pattern.")

                # Scroll down to load more videos
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Give time for the page to load more videos
            except Exception as e:
                print(f"Error scraping links: {e}")
                break

        driver.quit()

# Example usage
scrape_and_format_links(r"https://www.pexels.com/search/videos/skateboarding/", filename="pexels_videos.txt")