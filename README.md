# Text Summarizer
This text summarizer program reads text from different file formats (txt, doc, docx, pdf and epub) and generates a summary using OpenAI's GPT-3.5-turbo model.

## Prerequisites
Python 3.8 or higher
Install the required packages by running pip install -r requirements.txt.
Usage
Set the API_KEY environment variable with your OpenAI API key.

Add the summarization prompt to a file named prompt.txt. Make sure to include SUMMARY in the prompt where you want the summarized text to be inserted.


## Setup

Before running the script, make sure you have a folder called `working` in the same directory as the script. Place the input file (txt, doc, docx, or pdf) inside the `working` folder. The output file with the summary will also be saved in this folder.

## Usage

<pre>

python app.py input_file.ext
</pre>

The program will generate a summary and save it in a file named summary of {text}.txt, where {text} is a short sentence summarizing the whole text.

## Example
If you have a text file named sample.txt and you want to generate a summary, run:
<pre>

python app.py sample.txt
</pre>

The summary will be saved in a file named final_output.txt.

## Code Structure
read_txt(file_path): Reads and returns the content of a text file.
read_doc(file_path): Reads and returns the content of a Word document (doc or docx).
read_pdf(file_path): Reads and returns the content of a PDF file.
save_file(content, filename): Saves the content to a file with the given filename.
main(): The main function that handles the input file, reads the content, breaks it into chunks, and generates a summary for each chunk.
gpt3_completion(prompt, api_key, model='gpt-3.5-turbo', tokens=2000, max_retry=5): Generates a summary using the OpenAI API and GPT-3.5-turbo model.
