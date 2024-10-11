import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    return random.choice(user_agents)

def random_delay(min_delay=2, max_delay=7):
    time.sleep(random.uniform(min_delay, max_delay))

def collect_video_urls(links_folder, export_folder, max_retries=3):
    os.makedirs(export_folder, exist_ok=True)
    
    for filename in os.listdir(links_folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(links_folder, filename)
            export_filepath = os.path.join(export_folder, filename)
            
            with open(filepath, "r", encoding="utf-8") as f:
                links = f.readlines()

            for link in links:
                link = link.strip()
                if not link:
                    continue
                
                for retry in range(max_retries):
                    try:
                        options = uc.ChromeOptions()
                        options.add_argument(f'--user-agent={get_random_user_agent()}')
                        options.add_argument('--disable-blink-features=AutomationControlled')
                        options.add_argument('--disable-extensions')
                        options.add_argument('--no-sandbox')
                        options.add_argument('--disable-gpu')

                        driver = uc.Chrome(options=options)
                        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                            "source": """
                                Object.defineProperty(navigator, 'webdriver', {
                                    get: () => undefined
                                })
                            """
                        })
                        
                        random_delay()
                        driver.get(link)
                        
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, "challenge-form"))
                            )
                            print("Cloudflare challenge detected. Waiting...")
                            time.sleep(15)
                        except TimeoutException:
                            pass
                        
                        wait = WebDriverWait(driver, 20)
                        video_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'video[src$=".mp4"]')))
                        
                        actions = ActionChains(driver)
                        actions.move_to_element(video_element).perform()
                        random_delay(1, 3)
                        video_element.click()
                        
                        video_url = video_element.get_attribute("src")
                        
                        # Save the video URL immediately after collection
                        with open(export_filepath, "a", encoding="utf-8") as output_file:
                            output_file.write(video_url + "\n")
                        
                        print(f"Collected and saved: {video_url}")
                        break
                    except (TimeoutException, WebDriverException, requests.RequestException) as e:
                        print(f"Attempt {retry + 1}/{max_retries} failed for {link}. Error: {e}")
                        if retry < max_retries - 1:
                            print(f"Retrying in 2 seconds...")
                            time.sleep(2)
                    finally:
                        driver.quit()
                
                if retry == max_retries - 1:
                    print(f"Failed to collect video URL from {link} after {max_retries} attempts.")
                    # Save the failed link to a separate file
                    with open(os.path.join(export_folder, "failed_links.txt"), "a", encoding="utf-8") as failed_file:
                        failed_file.write(link + "\n")

# Example usage
links_folder = "pixabay_links"
export_folder = "video_urls"

collect_video_urls(links_folder, export_folder)