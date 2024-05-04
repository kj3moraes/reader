import chromadb
import chromadb.utils.embedding_functions as ef 
import pandas as pd

client = chromadb.PersistentClient(path="./.chroma")
collection = client.get_or_create_collection("blogs")

model = ef.InstructorEmbeddingFunction(
    model_name="hkunlp/instructor-xl"
)

# Embed all the blog posts
def embed_text(df: pd.DataFrame):
    # Concatenate the strings in the "topics", "content", and "title" columns
    df['embedded_text'] = df['Title'] + "\nTopics Dicussed " + df["Topics"] + "\n\nContent:" + df["Content"] 
    
    # Fit and transform the "embedded_text" column
    embedded_text_vectors = model.embed_with_retries(df["embedded_text"].to_list())
    
    # Convert the sparse matrix to a dense numpy array
    embedded_text_vectors = embedded_text_vectors.toarray()
    
    # Append the embedded text vectors to the DataFrame
    for i, row in enumerate(embedded_text_vectors):
        df.at[i, 'embedded_text'] = row
    
    return df

# Embed the authors by aggregating their posts
def embed_authors(df: pd.DataFrame):
    pass


df = pd.read_csv("./.data/topics-2.csv")
df = embed_text(df)

