import pyterrier as pt

if not pt.java.started():
    pt.java.init()

index_path = "./ikea_index"
index = pt.IndexFactory.of(index_path)

retriever = pt.BatchRetrieve(index, num_results=5, metadata=["docno", "title", "text", "raw_title", "raw_text"])

def search(query):
    results = retriever.search(query)
    
    print("Results DataFrame:")
    for _, row in results.iterrows():
        docno = row['docno']
        rank = row['rank']
        score = row['score']
        
        raw_title = row.get('raw_title', 'No raw title available')
        raw_text = row.get('raw_text', 'No raw text available')

        print(f"Rank: {rank} | docno: {docno} | raw_title: {raw_title} | raw_text: {raw_text} | score: {score}")

search("ikea bed")
