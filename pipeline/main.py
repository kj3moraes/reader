import pandas as pd
from pathlib import Path
from tqdm import tqdm
from utils import collect_all_markdown_files, process_file, query_summary_engine

DATA_PATH = Path("./.data")

# Collect all the markdown files
markdown_file_paths = collect_all_markdown_files(DATA_PATH)
data = []

# Process them and store them into a list of tuples
print(f"Started processing {len(markdown_file_paths)} markdown files")
for file_path in markdown_file_paths:
    metadata, content = process_file(file_path)
    
    author_name = metadata.get("Author Name", "No Name")
    publication_name = metadata.get("Publication Name", "No Pub Name")
    post_date = metadata.get("Post Date")
    title = metadata.get("Title", "No Title")
    subtitle = metadata.get("Subtitle", "No Title")
    content = title + subtitle + "\n\n" + content
    data.append((title, subtitle, author_name, publication_name, post_date, content))

# Save the dataframe locally
df = pd.DataFrame(data, columns=["Title", "Subtitle", "Author", "Publication", "Post Date", "Content"])
df.to_csv("./.data/presummary.csv")
print(f"Saved the presummary dataframe with {len(df.index)} entries")

# Iterate through all of the content and generate summaries
tqdm.pandas()
print("Attempting to summarize the entire dataset")
df["Summary"] = df["Content"].progress_apply(lambda x: query_summary_engine(x))
df.to_csv("./.data/train.csv")
print("Completed dataset generation")