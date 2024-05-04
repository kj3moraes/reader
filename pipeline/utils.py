import re

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

 
if __name__ == "__main__":
    import os
    for item in os.listdir("./.data"):
        if item.endswith(".md"):
            print(f"Processing {item}")
            with open("./.data/" + item, "r+") as infile:
                markdown_text = infile.read() 

            cleaned = clean_md(markdown_text)
                
            with open("./.data/" + item, "w") as outfile:
                outfile.write(cleaned)

#     original_text = """
# I’m sending this one out via email to all of you on the mailing list in order to get us all on the same page, but moving forward I will simply post the the audio to the site, which will also publish the episode to [Apple Podcasts](https://podcasts.apple.com/us/podcast/the-convivial-society/id1522126693) and [Spotify](https://open.spotify.com/show/4cbTb5qgTRCsDLW57na2iL?si=ff35bc883e924fb7).
#         """
#     print(original_text)
#     cleaned = clean_md(original_text)
#     print(cleaned)
    
#     with open("./.data/20230510_170318_why-an-easier-life-is-not-necessarily.md", "r+") as infile:
#         markdown_text = infile.read() 
#         cleaned = clean_md(markdown_text)
#         # print(cleaned)
#         infile.write(cleaned) 
