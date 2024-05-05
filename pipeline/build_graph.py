import json
from ast import literal_eval
from pydantic import BaseModel, RootModel
from tqdm import tqdm 
import chromadb

chroma_client = chromadb.PersistentClient(path="./.chroma")

collection = chroma_client.get_collection(name="blogs")

# Define the model for the nested "data" part
N_RESULTS = 10
DISTANCE_THRESHOLD = 8


class NodeData(BaseModel):
    title: str
    author: str
    topics: list
    authors_interest: list


class Node(BaseModel):
    id: str
    data: NodeData


class Link(BaseModel):
    source: str
    target: str


# # Get all embeddings
results = collection.get(ids=None,  include=["metadatas", "embeddings"], where={"type": {"$ne": "author"}})
if results["embeddings"] is None or results["metadatas"] is None:
    raise ValueError("No embeddings found in the collection")

nodes: list[Node] = []
links: list[Link] = []

# For each embedding, find the 5 nearest neighbors

for i, embedding in tqdm(enumerate(results["embeddings"]), total=len(results['embeddings'])):

    # Get the 5 nearest neighbors to the embedding
    # print(results["metadatas"][i])
    self_id = results["ids"][i]
    try:
        self_title = results["metadatas"][i]["title"]
        self_author = results["metadatas"][i]["author"] 
        self_topics = literal_eval(results["metadatas"][i]["topics"])
    except:
        continue

    query = collection.query(
        n_results=N_RESULTS,
        query_embeddings=[embedding],
        include=["metadatas", "distances"],
        where={
            "$and": [
                {"title": { "$ne": self_title }},
                {"type": "post"} 
            ]
        }
    )

    nearest_titles = [nearest_meta['title'] for nearest_meta in query["metadatas"][0]]

    if not query["distances"]:
        raise ValueError("No distances found in the query")
    distances = query["distances"][0]

    author_query = collection.query(
        n_results=2,
        query_embeddings=[embedding],
        include=["metadatas"],
        where={
            "$and": [
                {"name": { "$ne": self_author }}, 
                {"type":"author"}
            ]
        }
    )
    recs = [info['name'] for info in author_query['metadatas'][0]]

    source_id = results["ids"][i]
    # Add the node to the list of nodes
    new_node = Node(
        id=self_title,
        data=NodeData(
            title=self_title,
            author=self_author,
            topics=self_topics,
            authors_interest=recs
        )
    )
    # Add the node to the list of nodes
    nodes.append(new_node)

    for i, distance in enumerate(distances):
        if distance < DISTANCE_THRESHOLD:
            links.append(
                Link(
                    source=self_title,
                    target=nearest_titles[i]
                )
            )
    # break

# Dump to graphData.json
with open("graphData.json", "w") as f:
    json.dump({"nodes": [n.model_dump() for n in nodes],
               "links": [l.model_dump() for l in links]}, f)
