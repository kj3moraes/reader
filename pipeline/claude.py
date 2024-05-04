import pandas as pd 
from tqdm import tqdm
from utils import query_claude

df = pd.read_csv("./.data/train.csv")

def get_topics(text: str):
    dict = query_claude(text)
    topics = dict["topics"]
    return topics

tqdm.pandas()

df["Topics"] = df["Content"].progress_apply(lambda x: get_topics(x))

df.to_csv("./.data/topics.csv")