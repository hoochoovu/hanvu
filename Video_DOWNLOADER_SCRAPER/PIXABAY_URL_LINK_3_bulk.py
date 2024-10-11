import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

def scrape_video_links(search_term, output_folder="output", num_links=100):
    """
    Scrapes video links for a given search term and saves them to a text file.
    Cycles through pages until the desired number of links is reached.
    Excludes links containing the word "search" and avoids duplicates.
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Construct the URL and filename for the current search term
    url = f"https://pixabay.com/videos/search/{search_term}/?order=ec"
    filename = f"{search_term}.txt"
    
    # Create a file to store the links
    filepath = os.path.join(output_folder, filename)
    
    # Initialize browser
    driver = webdriver.Chrome()  # Assuming you have ChromeDriver installed
    links_found = 0
    page_num = 1
    unique_links = set()  # Use a set to keep track of unique links
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            while links_found < num_links:
                # Construct the URL for the current page
                current_url = url + f"&pagi={page_num}"
                try:
                    driver.get(current_url)
                    # Load the page fully
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    # Find all video links
                    video_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/videos/"]')
                    for element in video_elements:
                        link = element.get_attribute("href")
                        if link and "search" not in link:  # Exclude links with "search"
                            # Construct the full URL
                            full_link = "" + link
                            # Check if the link is unique
                            if full_link not in unique_links:
                                # Write the link to the file immediately
                                f.write(full_link + "\n")
                                f.flush()  # Ensure the link is written to the file
                                links_found += 1
                                unique_links.add(full_link)  # Add to the set of unique links
                                # Stop when desired number of links are found
                                if links_found >= num_links:
                                    break
                    # Increment page number for the next iteration
                    page_num += 1
                    # Scroll down to load more videos (optional, might not be necessary)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)  # Give time for the page to load more videos
                except Exception as e:
                    print(f"Error scraping links on page {page_num}: {e}")
                    break
    finally:
        driver.quit()

    print(f"Scraped {links_found} links for '{search_term}'")

# Example usage
output_folder = "pixabay_links"
num_links_to_scrape = 100
search_terms = ["beach", "hiking", "waterfall" ]  # Add your desired search terms here
#"beach", "ocean", "sky", "stars", "time-lapse","hiking", "exercise", "nature", "buddha", "rock-climbing", "waterfall", "stream", "sunset", "forest", "animals", "rain", "autumn", "snow", "mountains", "road", "trees", "river", "lake", "rocks", "flowers", "boat", "sunrise"
for term in search_terms:
    scrape_video_links(term, output_folder, num_links_to_scrape)