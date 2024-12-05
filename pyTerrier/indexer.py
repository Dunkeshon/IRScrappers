import pyterrier as pt
import pandas as pd
from pymongo import MongoClient

if not pt.java.started():
    pt.java.init()

client = MongoClient("mongodb://localhost:27017/")
db = client["IR_Ikea"]
reviews_collection = db["reviews"]
articles_collection = db["articles"]

def get_documents(collection):
    docs = collection.find()
    documents = []
    for doc in docs:
        docno = str(doc["_id"])
        title = doc.get("articleTitle", "No title available")
        text = doc.get("articleText", "No text available")
        print(f"Document ID: {docno}, Title: {title}, Text: {text}")
        documents.append({"docno": docno, "title": title, "text": text})
    return pd.DataFrame(documents)

reviews_df = get_documents(reviews_collection)
articles_df = get_documents(articles_collection)

all_docs_df = pd.concat([reviews_df, articles_df])

index_path = "./ikea_index"
indexer = pt.IterDictIndexer(index_path, meta={'docno': 24, 'title': 50, 'text': 1000})

indexer.index(all_docs_df[['docno', 'text', 'title']].to_dict(orient="records"))

print(f"Indexing complete! Index stored at: {index_path}")
