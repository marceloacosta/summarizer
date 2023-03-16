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
    output_folder = "working"
    output_path = os.path.join(output_folder, filename)
    with open(output_path, "w") as file:
        file.write(content)

def main():
    parser = argparse.ArgumentParser(description='Read text from different file formats')
    parser.add_argument('file', help='Path to the file to read text from')
    args = parser.parse_args()

    input_folder = "working"
    file_path = os.path.join(input_folder, args.file)
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
        "messages":[
        {"role": "system", "content": "Please extract and convey the core message of the content without using any phrases like 'the article' 'the text', 'the content' or similar terms. Focus on describing the key idea or concept presented. Preserve important details."},
        {"role": "system", "name":"example_user", "content": "Students  Gain real-world experience by building your own small projects.  Find ideas for your school projects or your rst portfolio. 9GENERATING PRODUCT IDEAS Introducing the idea generation framework Problems rst, products second It is a common belief in the startup community that the best ideas are organic. This means that ideas grow from your own experience and from solving your own problems. Some of the following techniques will help you to extract such problems, and some will lead you to nd interesting opportunities. For me, nding these opportunities is one way to expose myself to new and interesting problems to solve. Tomer Sharon, in his book, Validating Product Ideas, interviewed 200 product managers and founders, and discovered that, while 198 of them had a list of ideas, only two had a list of problems. The latter is a much better approach for several reasons, one of which is that problems potentially have multiple solutions (and, therefore, could generate multiple products). It means that focusing on problems can potentially lead to more product ideas. Having many ideas can increase the chances of nding successful ideas just by having a wider variety to choose from. So, to have more and better ideas and to increase your chances of business success, always be aware of the problem youre trying to solve. Why use this framework? Below youll nd 17 techniques that help you to generate product ideas. This framework has two goals: 10INTRODUCING THE IDEA GENERATION FRAMEWORK 1. To generate ideas immediately  Methods like these are a great way to lead the thought process in specic directions by adding constraints. Take some time to go through the techniques and put effort into following them and writing down the ideas you come up with. You will build a list of ideas quickly and, later on, you can assess them properly and pick the most promising ones. 2. To create ideation mental models in your mind  Putting these techniques to the back of mind, once"},
        {"role": "system", "name": "example_assistant", "content": "To generate successful product ideas, it is important to focus on problems rather than products. This approach can potentially lead to multiple solutions and increase the chances of finding successful ideas. There are 17 techniques to generate product ideas and emphasizes the importance of creating ideation mental models in your mind. By following these techniques and writing down the ideas, one can quickly build a list of ideas and assess them later to pick the most promising ones."},
        {"role": "user", "content": prompt},
    ],



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
