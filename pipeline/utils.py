import re
import os
from typing import Tuple
import json
import anthropic
from ast import literal_eval
from dotenv import load_dotenv
import requests as req
from pathlib import Path

# Constants
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_URL = os.getenv("API_URL")


def clean_html(markdown_txt: str):
    # Regular expression pattern to match HTML tags
    pattern = r'<.*?>'
    
    # Replace HTML tags with an empty string
    cleaned_text = re.sub(pattern, '', markdown_txt)
    
    return cleaned_text


def clean_formatting(markdown_txt: str):

    text = markdown_txt
    # Remove bold formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\_\_(.*?)\_\_', r'\1', text)
    
    # Remove italic formatting
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'\_(.*?)\_', r'\1', text)

    # Remove images 
    pattern = r'\[!\[\]\(https?://[^\)]+\)\]\(https?://[^\)]+\)'
    text = re.sub(pattern, '', text, flags=re.MULTILINE)
    text = re.sub(r'!\[\]\(https?://[^\)]+\)', '', text, flags=re.MULTILINE)
    
    # Remove links
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    # Remove quotes
    text = re.sub(r'>\s?', '', text)
    
    # Remove extra newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text.strip()


def clean_md(markdown_txt: str):
    text = markdown_txt
    text = clean_html(text) 
    text = clean_formatting(text)

    return text.lower()


def collect_all_markdown_files(path: Path) -> list[Path]:
    """ Given a path to a directory, it will collect all the markdown files 
        present in that directory recursively
        
    Args:
        path (Path): path to a directory

    Returns:
        list[Path]: list of Paths to all the markdown files present in the
                    directory. 
    """

    markdown_file_paths = []
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".md"):
                markdown_file_paths.append(Path(dirpath) / filename)
            
    return markdown_file_paths 


def process_file(file_path: Path) -> Tuple[dict, str]:

    raw_text = file_path.open("r").read()
    # Split the text into metadata and content sections
    sections = re.split(r'\n---\n', raw_text, maxsplit=2)

    # Parse the metadata section
    metadata_lines = sections[1].strip().split('\n')
    metadata = {}
    for line in metadata_lines:
        try:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
        except:
            continue
    # Extract the content section
    content = sections[2].strip()
    cleaned_content = clean_md(content)
    return metadata, cleaned_content


def query_summary_engine(original_text: str):
    headers = {
        "Accept" : "application/json",
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json" 
    }
    payload = {
        "inputs": original_text,
        "parameters": {}
    }
    response = req.post(API_URL, headers=headers, json=payload) 
    if response.status_code != 200:
        raise Exception("Failed to query the summary engine")
    data = response.json()
    return data[0]["summary_text"]


def query_claude(original_text: str) -> dict[str, list]:
    """ Queries Claude 3 Haiku for the topics and the references made in the provided text

    Args:
        original_text (str): The text to be analyzed 

    Returns:
        dict[str, list]: a dictionary of the following kind
                            {
                                "topics": [...]
                                "references": [...]
                            } 
    """ 

    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
    )

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system="""
                You are a topic identification bot. You are tasked with reading a text and coming up
                with topics that are discussed in the text or abstract concepts. These should be short and terse.
                If there any authors referenced, add them as well. Answer ONLY in JSON with 2 keys, "topics" and "references" like so
                {
                    "topics": []
                    "references": []
                } 
                """,
        messages=[
            {"role": "user", "content": f"The text is provided below \n{original_text}"}
        ]
    )
    response = message.content[0].text
    try:
        dict = literal_eval(response) 
    except:
        dict = {"topics": [], "references": []}
    return dict

if __name__ == "__main__":
    import os
    example_text = Path("./.data/culture_study/20201011_185302_youre-still-not-working-from-home.md").read_text()
    cleaned_text = clean_md(example_text)
    print(query_claude(cleaned_text))
    # for item in os.listdir("./.data"):
    #     if item.endswith(".md"):
    #         print(f"Processing {item}")
    #         with open("./.data/" + item, "r+") as infile:
    #             markdown_text = infile.read() 

    #         cleaned = clean_md(markdown_text)
                
    #         with open("./.data/" + item, "w") as outfile:
    #             outfile.write(cleaned)
