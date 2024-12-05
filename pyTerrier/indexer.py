import pyterrier as pt
from pymongo import MongoClient

# Initialize PyTerrier
if not pt.started():
    pt.init()

def fetch_data_from_mongo():
    """Fetch data from MongoDB."""
    client = MongoClient('localhost', 27017)
    db = client.IR_Ikea
    reviews_collection = db.reviews
    return list(reviews_collection.find())

def create_index():
    """Create an index using PyTerrier."""
    reviews = fetch_data_from_mongo()

    # Prepare documents with title and text as metadata
    valid_docs = [
        {"docno": str(idx), 
         "text": item["articleText"], 
         "title": item["articleTitle"], 
         "metadata": {"title": item["articleTitle"], "text": item["articleText"]}}  # Adding metadata
        for idx, item in enumerate(reviews) if item.get("articleText") and item.get("articleTitle")
    ]

    # Use IterDictIndexer to index the documents
    indexer = pt.IterDictIndexer("./ikea_reviews_index")
    
    # Index the documents
    index_ref = indexer.index(valid_docs)
    print(f"Indexing complete! Index stored at: {index_ref}")
    return index_ref

if __name__ == "__main__":
    create_index()
