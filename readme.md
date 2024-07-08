These are the collections of Python programs written with the assistance of AI. They are a small suite of tools I used during the learning process for AI as well as Automation.

>File Organization Code: is a collection of small programs each with a purpose of organizing, moving, deleting, renaming, tokenizing, captioning, concatenating or decatenating. Useful to process large numbers of files for Dataset training/formatting.

>Pexels Downloader (webscraping): Are two programs - First program downloads URL links associated with a particular search on Pexels Website into a .txt file. The second program downloads those links one by one until the txt files are iterated through in a folder. Useful for scraping videos for free from copyright to use for anything (social media, content creation, training, etc).

>Shopify Web Image Scraper for BYLT: This is 3 smaller programs in one. It downloads the colors, title style, and images and organizes them into a folder. I used this scrape 10,000 images for dataset training (machine learning for Stable Diffusion) to generate images related to this fashion brand. (www.byltbasics.com) The code should work for their site, assuming nothing has changed with their code structure.

>Video Maker Programs: There are two APIs and two programs that generate content here to ultimately make a video by stitching the content together.

1. First program "Quote List Extractor Program" extracts quotes from a txt file and saves each quote into a text file.
2. Google Gemini API program then takes texts from that folder and then automatically generates content based on the quote or topic and saves result to a text file.
3. Eleven Labs API takes the Gemini results and creates a TextToSpeech Audio file of the generated output into .mp3
4. Video Maker program takes the Generated Audio from ElevenLabs and stitches together background videos (e.g. from Pexels) and music directory to make a complete video.

The idea is to automate as much of the video content creation process as possible to save time and editing.

>All-In-One Auto Video Maker: This program combines all 4 steps into program so that it iterates through multiple work files.
In case there is an error after the Audio is generated but the video maker program errors out, there is an extra program in here called AudioGen Fixer which takes that audio file and tries to make the video again. This is so that we don't waste Audio credits from ElevenLabs since it is already created.