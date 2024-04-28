import anthropic
from dotenv import load_dotenv
import os
from utils import clean_md

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
)

with open("./.data/test.md", "r+") as infile:
    markdown_text = infile.read()

cleaned = clean_md(markdown_text)

message = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1024,
    system="""  You are a topic identification bot. You are tasked with reading a text and coming up
                with topics that are discussed in the text or abstract concepts. These should be short and terse.
                If there any authors referenced, add them as well. Answer in JSON with 2 keys, "topics" and "references" like so
                {
                    "topics": []
                    "references": []
                }
                """,
    messages=[
        {"role": "user", "content": f"The text is provided below \n{cleaned}"}
    ]
)

print(message.content[0].text)