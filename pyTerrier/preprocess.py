from utils import get_documents, preprocess_data, preprocess_text
from pymongo import MongoClient
import pandas as pd

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["IR_Ikea"]

# Collections for raw data
reviews_collection = db["reviews"]
articles_collection = db["articles"]
articles2_collection = db["articles2"]

# Retrieve raw documents and combine them
reviews_df = get_documents(reviews_collection)
articles_df = get_documents(articles_collection)
articles2_df = get_documents(articles2_collection)
df = pd.concat([reviews_df, articles_df, articles2_df])

# Preprocess data while keeping raw fields
print("Preprocessing title and text")
df['raw_title'] = df['title']
df['raw_text'] = df['text']
df['link'] = df['link']
df['title'] = df['title'].apply(preprocess_text)
df['text'] = df['text'].apply(preprocess_text)

# Save preprocessed data with original fields into MongoDB
processed_collection = db["processed_documents"]
processed_documents = df[['docno', 'title', 'text', 'raw_title', 'raw_text', 'link']].to_dict(orient='records')
processed_collection.insert_many(processed_documents)
print("Preprocessed data with original fields saved in MongoDB under 'processed_documents' collection")
