from rest_framework.decorators import api_view
from rest_framework.response import Response
import pyterrier as pt
import os
from django.conf import settings
import pandas as pd

# Ensure PyTerrier is initialized
if not pt.started():
    pt.init()

# Define the PyTerrier index path
index_path = os.path.join(settings.BASE_DIR, "..", "pyTerrier", "ikea_index")
index = pt.IndexFactory.of(index_path)
retriever = pt.BatchRetrieve(index, metadata=["docno", "title", "text", "raw_title", "raw_text", "link"])

# Global dictionaries to persist feedback and adjusted scores
feedback_store = {}
adjusted_scores = {}

@api_view(['POST'])
def search_view(request):
    query = request.data.get('query', '')
    feedback = request.data.get('feedback', {})  # Example: {"docno1": "relevant", "docno2": "irrelevant"}

    if not query:
        return Response({"error": "Query parameter is required"}, status=400)

    try:
        # Step 1: Initialize scores for the query if not already present
        if query not in adjusted_scores:
            adjusted_scores[query] = {}

        # Step 2: Perform search
        results = retriever.search(query)

        # Step 3: Use existing adjusted scores or initialize with current results
        for idx, row in results.iterrows():
            docno = row['docno']
            # Retain existing adjusted score or initialize to the current score
            if docno not in adjusted_scores[query]:
                adjusted_scores[query][docno] = row['score']
            results.at[idx, 'score'] = adjusted_scores[query][docno]

        # Step 4: Apply feedback from the current request
        for idx, row in results.iterrows():
            docno = row['docno']
            current_score = adjusted_scores[query][docno]

            # Adjust score only if feedback is provided for this document
            if docno in feedback:
                if feedback[docno] == "relevant":
                    current_score *= 1.5  # Incremental boost
                elif feedback[docno] == "irrelevant":
                    current_score *= 0.5  # Incremental penalty
                adjusted_scores[query][docno] = current_score  # Persist adjusted score
                results.at[idx, 'score'] = current_score

        # Step 5: Re-sort by updated scores
        results = results.sort_values(by="score", ascending=False)

        # Step 6: Format response
        data = results[['docno', 'raw_title', 'raw_text', 'score', 'link']].to_dict(orient='records')
        return Response(data)

    except Exception as e:
        return Response({"error": f"Internal Server Error: {str(e)}"}, status=500)
