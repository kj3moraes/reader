import re

def clean_html(markdown_txt: str):
    # Regular expression pattern to match HTML tags
    pattern = r'<.*?>'
    
    # Replace HTML tags with an empty string
    cleaned_text = re.sub(pattern, '', markdown_txt)
    
    return cleaned_text


def clean_formatting(markdown_txt: str):
    # Remove bold formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', markdown_txt)
    
    # Remove italic formatting
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # Remove links
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    # Remove quotes
    text = re.sub(r'>\s?', '', text)
    
    # Remove extra newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text.strip()


def clean_md(markdown_txt: str):
    text = clean_html(markdown_txt) 
    text = clean_formatting(markdown_txt)

    return text.lower()

 
if __name__ == "__main__":
    import os
    with open("./.data/test.md", "r+") as infile:
        markdown_text = infile.read()
    
    cleaned = clean_md(markdown_text)

    with open("./.data/out.md", "w+") as outfile:
        outfile.write(cleaned)