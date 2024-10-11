import os
import google.generativeai as genai

# Access your API key as an environment variable.
genai.configure(api_key="id_key")
# Choose a model that's appropriate for your use case.
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = "Write a story about a magic backpack."

response = model.generate_content(prompt)

print(response.text)
