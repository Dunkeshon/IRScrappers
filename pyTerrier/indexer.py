import pyterrier as pt
import pandas as pd
from pymongo import MongoClient

if not pt.java.started():
    pt.java.init()

client = MongoClient("mongodb://localhost:27017/")
db = client["IR_Ikea"]
processed_collection = db["processed_documents"]

processed_df = pd.DataFrame(list(processed_collection.find()))

index_path = "./ikea_index"
indexer = pt.IterDictIndexer(index_path, meta={'docno': 24, 'title': 50, 'text': 5000, 'raw_title': 100, 'raw_text': 5000, 'link': 200})

indexer.index(processed_df[['docno', 'title', 'text', 'raw_title', 'raw_text', 'link']].to_dict(orient="records"))

print(f"Indexing complete! Index stored at: {index_path}")