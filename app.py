from dotenv import load_dotenv
import os
import argparse
from docx import Document
import pdfplumber
import textwrap
from time import time, sleep
import json
import re
import requests


load_dotenv()

api_key = os.environ.get("API_KEY")


def read_txt(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def read_doc(file_path):
    doc = Document(file_path)
    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

def read_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def save_file(content, filename):
    with open(filename, "w") as file:
        file.write(content)

def main():
    parser = argparse.ArgumentParser(description='Read text from different file formats')
    parser.add_argument('file', help='Path to the file to read text from')
    args = parser.parse_args()

    file_path = args.file
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == '.txt':
        text = read_txt(file_path)
    elif file_ext == '.doc' or file_ext == '.docx':
        text = read_doc(file_path)
    elif file_ext == '.pdf':
        text = read_pdf(file_path)
    else:
        print(f"Error: The file format {file_ext} is not supported.")
        return

    chunks = textwrap.wrap(text, 2000)
    result = list()
    count = 0
    for chunk in chunks:
        count = count + 1
        with open("prompt.txt", "r") as file:
            prompt = file.read().replace('<<SUMMARY>>', chunk)
        prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
        summary = gpt3_completion(prompt, api_key)
        print('\n\n\n', count, 'of', len(chunks), ' - ', summary)
        result.append(summary)
    save_file('\n\n'.join(result), 'final_output_%s.txt' % time())

def gpt3_completion(prompt, api_key, model='gpt-3.5-turbo', tokens=2000, max_retry=5):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    url = "https://api.openai.com/v1/chat/completions"
    retry = 0

    while True:
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()

            text = result['choices'][0]['message']['content'].strip()
            text = re.sub('\s+', ' ', text)

            filename = f"{time()}_gpt3.txt"
            with open(f"gpt3_logs/{filename}", "w") as outfile:
                outfile.write(f"PROMPT:\n\n{prompt}\n\n==========\n\nRESPONSE:\n\n{text}")

            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return f"GPT3 error: {oops}"
            print(f"Error communicating with OpenAI: {oops}")
            sleep(1)

if __name__ == '__main__':
    main()
