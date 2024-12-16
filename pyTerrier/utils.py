import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

def preprocess_text(text):
    """ Tokenizes, lowercases, removes stopwords, and applies stemming to the text """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Convert to lowercase
    text = text.lower()
    # Tokenize
    tokens = text.split()
    # Remove stopwords and apply stemming
    tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]
    return " ".join(tokens)

def filter_empty_docs(df):
    """ Filters out documents with empty title or text """
    return df[(df['title'].str.strip() != '') & (df['text'].str.strip() != '')]

def preprocess_data(df):
    """ Preprocess title and text fields """
    df['title'] = df['title'].apply(preprocess_text)
    df['text'] = df['text'].apply(preprocess_text)
    df = filter_empty_docs(df)
    return df

def get_documents(collection):
    """ Retrieves documents from MongoDB collection """
    docs = collection.find()
    documents = []
    for doc in docs:
        docno = str(doc["_id"])
        title = doc.get("articleTitle", "No title available")
        text = doc.get("articleText", "No text available")
        link = doc.get("articleLink", "No link available")
        documents.append({"docno": docno, "title": title, "text": text, "link": link})
    return pd.DataFrame(documents)
