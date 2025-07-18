# import os
# import google.generativeai as genai
# from dotenv import load_dotenv


# load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

import google.generativeai as genai

genai.configure(api_key="XXX")


def summarize_with_gemini(text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Summarize the following changelog in 3 bullet points:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text
