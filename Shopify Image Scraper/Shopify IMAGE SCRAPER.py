import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import Chrome
import io
import time
import re
import os

# Initialize a Chrome WebDriver object
service = Service(executable_path='G:\\ScrapeSCRAPE\\chromedriver_win32\\chromedriver.exe') 
driver = webdriver.Chrome(service=service)


# Specify the parent folder where the image folders should be created
parent_folder = "PARENT FOLDER DIR"

# Create a text list to store the URLs
urls = []
# Create a text list to store the titles
titles = []
title_text = ''
file_text = '' 
# Create a text list to store the colors
colors = []
color_text = ''
color = ''
name = ''
desc = ''
folder_name = []
colors = []
names = []
url_list = []
loop = 0
imgloop = 0
images = []


# Read URLs from a text file
with open("URLS.txt", "r") as file:
    url_list = file.readlines()
url_list = [url.strip() for url in url_list]

for url in url_list:
# Define the webpage to go to
    # Proxy info
    proxy = f"YOUR PROXY INFO HERE"
    response = requests.get(url, proxies={'http': proxy, 'https': proxy})
    print('Starting Proxy')
    time.sleep(3)  # Adding a delay of 2 seconds
    # Open the website in the Chrome browser
    driver.get(url)
    print('Loading Page')
    time.sleep(5)  # Adding a delay of 2 seconds
    # Parse the HTML from the URL
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    print('Starting Loop')
    time.sleep(2)  # Adding a delay of 2 seconds
           
    # ######******THIS IS THE SWATCH STRIPPER******######
    # Step 1: Find div tags with class names containing "option option-color"
    color_tags = driver.find_elements(By.CSS_SELECTOR, "div[class*='option option-color']")
    
    # Step 2: Find div tags with class names containing "swatch-Color"
    div_tags = driver.find_elements(By.CSS_SELECTOR, "div[data-v-1d7925be=''][class*='swatch-Color not-selected'], div[data-v-1d7925be=''][class*='swatch-Color selected'],div[data-v-5a7b6834=''][class*='swatch-Color not-selected'], div[data-v-5a7b6834=''][class*='swatch-Color selected']")

    h3_tags = driver.find_elements(By.CSS_SELECTOR, "h3[data-v-5b1108e4=''][class*='option-label']")

    # ######******THIS IS THE IMAGE STRIPPER******######
    img_tags = driver.find_elements(By.CSS_SELECTOR, "div[class='nacelle-image']")
    #img_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-v-b999f23ae=''][class='media-select-view columns is-multiline nacelle']")
    print(img_tags)
    print('Finding Div Tags')

    ######******THIS IS THE INITIAL TITLE STRIPPER******######
    # Find the title element and extract the text 
    title_element = soup.find('h1', class_='product-title nacelle')
    if title_element:
        title_text = title_element.text.strip()
        titles.append(title_text)
        loop += 1
        print(title_text)
        print('URL appended to ', title_text , ' to swatch_titles.txt file')
        time.sleep(2)  # Adding a delay of 2 seconds
    
    ######******THIS IS THE INITIAL COLOR STRIPPER******######
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Find the title element and extract the text 
    span_element = soup.find('span', class_='option-selected')
    #span_element = div_tag.find_element(By.CSS_SELECTOR, "span.option-selected")
    print(span_element)
    if span_element:
        color_text = span_element.text.strip()
        colors.append(color_text)
        loop += 1
        print(color_text)
        print('Color Selection appended to ', color_text , ' to swatch_colors.txt file')

    def imagedown(folder, parent_folder):
        global imgloop
        global desc
        global file_text

        folder_path = os.path.join(parent_folder, folder)
        print(folder_path)
        try:
            os.mkdir(folder_path)
        except FileExistsError:
            pass
        os.chdir(folder_path)

        #soup = BeautifulSoup(driver.page_source, 'html.parser')
        #images = img_tags.find_all('img')

        ##########HERE WE SEARCH INSIDE OF THE SPECIFIC DIV TAGS HTML AN EXTRA LAYER DEEPER###########
        # ######******THIS IS THE IMAGE STRIPPER******######
        img_tags = driver.find_elements(By.CSS_SELECTOR, "div[class='nacelle-image']")
        images = []
        processed_urls = set()
        for img_tag in img_tags:
            html_source = img_tag.get_attribute('innerHTML')
            soup = BeautifulSoup(html_source, 'html.parser')
            img_elements = soup.find_all('img')
            
            # Append the found <img> tags to the 'images' list
            images += img_elements           
        
        for image in images:
            if image['src'] in processed_urls:
                continue
            
            if image['src'].endswith('.svg') or 'vercel' in image['src'] or 'icon' in image['src'] or 'tags' in image['src']:
                continue 

            processed_urls.add(image['src'])
            images.append(image)
            
            file_text = title_text.replace(':', '').replace('3/4', '').replace('/', ' ')
            desc = 'Bylt '+ color_text.replace('/', ' ') + ' - ' + file_text + ' - ' + str(imgloop)
            imgloop +=1
            link = image['src']
            try:
                response = requests.get(link)
                response.raise_for_status()
                with open(desc + '.jpg', 'wb') as f:
                    f.write(response.content)
                print('Downloaded:', desc)

            except Exception as e:
                error_message = "An error occurred while downloading the image: " + str(e) + "\n"
                with open("error_log.txt", "a") as error_file:
                    error_file.write(error_message)
                pass
            
                
                        
    #imagedown(file_text, parent_folder)
    #imgloop = 0              


    # Step 3: Click on each div tag and copy the URL from the browser
    for div_tag in div_tags:
                          
        action = ActionChains(driver)
        #driver.execute_script("arguments[0].scrollIntoView();", div_tag)
        driver.execute_script("arguments[0].click();", div_tag)
        time.sleep(2)  # Adding a delay of 2 seconds

        ######******THIS IS THE TITLE STRIPPER******######
        # Find the title element and extract the text 
        title_element = soup.find('h1', class_='product-title nacelle')
        if title_element:
            title_text = title_element.text.strip()
            titles.append(title_text)
            loop += 1
            print(title_text)
            print('URL appended to ', title_text , ' to swatch_titles.txt file')
         # Step 3: Click on each div tag and copy the URL from the browser
        
        
        for h3_tag in h3_tags:
            print(h3_tag)            
                    
            # Parse the HTML after clicking on the elements
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            #time.sleep(1)  # Adding a delay of 1 seconds

            ######******THIS IS THE COLOR STRIPPER******######
            # Find the title element and extract the text 
            span_element = soup.find('span', class_='option-selected')
            #span_element = div_tag.find_element(By.CSS_SELECTOR, "span.option-selected")
            print(span_element)
            if span_element:
                color_text = span_element.text.strip()
                colors.append(color_text)
                loop += 1
                print(color_text)
                print('Color Selection appended to ', color_text , ' to swatch_colors.txt file')
                break 

        file_text = title_text.replace(':', '').replace('3/4', '').replace('/', ' ')
        imagedown(file_text, parent_folder)
        imgloop = 0

                


    

    loop += 1


#imagedown(url, folder_name)               
print(loop, ' Pages Downloaded Complete')