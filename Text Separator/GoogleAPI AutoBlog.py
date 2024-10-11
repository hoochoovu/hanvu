import os
import time
import google.generativeai as genai

# Access your API key as an environment variable.
genai.configure(api_key="id_key")
# Choose a model that's appropriate for your use case.
model = genai.GenerativeModel('gemini-1.5-flash')

# Folder paths
input_folder = r"E:\Python_Practice\Text Separator\text"
output_folder = r"E:\Python_Practice\Text Separator\Output"

# Custom text field
custom_text = """[Role] You are a professional, popular blog writer who writes daily wisdom based on philosophy, particularly Stoicism. The idea of the blog is to help people understand Stoicism better through daily quote analysis. This whole response should be written so that it sounds less like written by AI. The output should be like below without any numbering/bulleting, extra commentary by you, and just output the data only.

[Task] 
1.  Firstly, repeat and copy the original quote with the author name. Then give the quote a catchy title.  Examples: 'Follow this advice to avoid..X', 'Do this to stop feeling..X', 'Stop this habit if you want to..X', 'Learn this skill if you want to have..X'.
2.  Write a short 1-sentence description relating to the quote.
3.  Provide an accurate, simple, and concise modern translation of the quote.
4.   Write the best engaging question to ask a viewer based on the quote.
5.   Explain the Stoic quote so it is simple and easily understood.
6.   Write 5 paragraphs that elaborate on the quote, in the speech style of great presidents and leaders. Use references to other Stoics or philosophers from the list: Marcus Aurelius, Seneca, Epictetus, Rufus Musonius, Zeno of Citium, Cicero, Cato the Younger, Aristotle, Heraclitus, Plato, Socrates, Chryssipus, Cleanthes, Hierocles, Thales, Xenophon, Descartes, Diogenes, Hippocrates, Democritus, or other supporting Stoicism/philosophy knowledge to support and fill the content in relation to the quote. Any supporting quotes must be commonly attributed to the author being used. This section should find opportunities to naturally use long-tail keywords related to Stoicism whenever possible and context relevant. Each paragraph needs to be at least 4 sentences long.
7.   Give real-world examples with a modern connection. Find additional cross-references and examples from a movie, scene, plot, a book, a story, a poem, a song, an article, a show, a celebrity, or famous figure in history that directly supports this quote. Connect Stoicism to the real world in a meaningful way and keep the content engaging. Additionally, if you find other examples in the real modern world, then go ahead and list them here. This section should sound like a personal analysis of how Stoicism fits into the modern world, making major connecting points to our current world. If referencing a general group of people (like athletes, for example), reference a famous figure or celebrity if possible (e.g., an example celebrity, sports figure, athlete, or famous figure depending on the context). Use context to determine the appropriate candidate to mention. This section must be factual, real, and cross-checked for accuracy. Write 2 paragraphs here and talk more about the referenced content.

The output should be text only with no special formatting, headers, or markers.
"""

# Check if the input folder exists
if not os.path.exists(input_folder):
    print(f"Error: Input folder not found: {input_folder}")
    exit()

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Iterate through all files in the input folder
for filename in os.listdir(input_folder):
    # Check if the file is a .txt file
    if filename.endswith(".txt"):
        # Construct the full file path
        filepath = os.path.join(input_folder, filename)

        # Open the file and read its contents
        with open(filepath, "r", encoding='utf-8') as f:  # Use utf-8 encoding
            file_content = f.read()

        # Construct the prompt
        prompt = f"{file_content}\n\n{custom_text}"

        # Generate response from the API
        response = model.generate_content(prompt)

        # Construct the output file name
        output_filename = f"[Complete]-{filename}"
        output_filepath = os.path.join(output_folder, output_filename)

        # Save the response to the output file
        with open(output_filepath, "w", encoding='utf-8') as f:  # Use utf-8 encoding
            f.write(response.text)

        print(f"Processed file: {filename}")
        time.sleep(15)