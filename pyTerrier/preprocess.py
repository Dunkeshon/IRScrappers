from utils import get_documents, preprocess_data
from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://localhost:27017/")
db = client["IR_Ikea"]
reviews_collection = db["reviews"]
articles_collection = db["articles"]

reviews_df = get_documents(reviews_collection)
articles_df = get_documents(articles_collection)

df = pd.concat([reviews_df, articles_df])

print("Preprocessing title and text")
df = preprocess_data(df)

processed_collection = db["processed_documents"]

processed_documents = df[['docno', 'title', 'text']].to_dict(orient='records')
processed_collection.insert_many(processed_documents)

print("Preprocessed data saved in MongoDB")