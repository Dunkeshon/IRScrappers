import pyterrier as pt

if not pt.java.started():
    pt.java.init()

index_path = "./ikea_index"
index = pt.IndexFactory.of(index_path)

retriever = pt.BatchRetrieve(index, num_results=5, metadata=["docno", "title", "text"])

def search(query):
    results = retriever.search(query)
    
    print("Results DataFrame:")
    for _, row in results.iterrows():
        docno = row['docno']
        rank = row['rank']
        score = row['score']
        
        title = row.get('title', 'No title available')
        text = row.get('text', 'No text available')

        print(f"Rank: {rank} | docno: {docno} | title: {title} | text: {text} | score: {score}")

search("ikea")
