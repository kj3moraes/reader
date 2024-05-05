import chromadb
import anthropic
import json
from ast import literal_eval
from tqdm import tqdm
from dotenv import load_dotenv
import hashlib
import chromadb.utils.embedding_functions as ef 
import pandas as pd
import os

load_dotenv()
client = chromadb.PersistentClient(path="./.chroma")
collection = client.get_or_create_collection("blogs")
claude = anthropic.Client(
    api_key=os.getenv("ANTHROPIC_API_KEY") 
)

def prompt(text: str, system_prompt: str):
    text = "No works present" if text == "" else text 
    response = claude.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role":"user", "content": text}  
        ]
    ) 

    return response.content[0].text
    

def generate_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# Embed all the blog posts
def embed_text(df: pd.DataFrame):
    """ Embeds the title and topics of the Dataframe and upserts them into the vector database. 
    """
    
    # Fit and transform the "embedded_text" column
    for index, _ in tqdm(df.iterrows(), total=df.shape[0]):
        title = df['Title'][index]
        topics = df['Topics'][index]
        author = df['Author'][index]

        embedded_text = f"{title} \n\ntopics discussed{topics}"
        collection.upsert(
            ids=generate_hash(embedded_text),
            documents=embedded_text,

            # topics here is a list serialized as a string. We need to store it this way because chroma 
            # does not allow lists in metadata.
            metadatas={"title":title, "author": author, "topics": topics, "type":"post"}
        ) 

# Embed the authors by aggregating their posts
def embed_authors(df: pd.DataFrame):
    """Embeds all the authors information by agglomerating the topics they discuss
    """ 
    _prompt = """
    You will be provided with a list of an author's works along with the topics discussed in each and every one 
    of them. Your task is to make a list of 10 of the most relevant topics the author talks about.
    Remember, you can think and add more abstract / complex concepts that you feel the author would talk about but
    you must only give a valid JSON object as a response. 
    """

    author_names = df["Author"].unique()   
    print(author_names)
    
    for author in tqdm(author_names, total=len(author_names)):
        author_df = df[df["Author"] == author]
        works = [] 
        for index, row in author_df.iterrows():
            post_title = author_df["Title"][index]
            post_topics = literal_eval(author_df["Topics"][index])
            works.append(f"{author} talks about {post_topics[:6]} in their blog post {post_title}")
        # if there are no works to report on then no need to upsert.
        if works == []:
            continue 
        response = prompt('\n'.join(works), _prompt) 
        collection.upsert(
            ids=generate_hash(author),
            documents=response,
            metadatas={"type":"author", "name": author}
        )


df = pd.read_csv("./.data/topics-2.csv")
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Embed all the blog posts 
print("Embedding all the blog posts")
# embed_text(df)

# # Embed the authors too with a special field in the metadata
print("Embedding all the authors information")
embed_authors(df)

# query = "Friendship"
# response = collection.query(
#     query_texts=query,
#     where={"type":"author"},
#     n_results=2
# )
# print(response)