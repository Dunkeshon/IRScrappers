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
retriever = pt.BatchRetrieve(index, num_results=10, metadata=["docno", "title", "text", "raw_title", "raw_text", "link"])

# Global dictionary to persist feedback (mock session for simplicity)
feedback_store = {}

@api_view(['POST'])
def search_view(request):
    query = request.data.get('query', '')
    feedback = request.data.get('feedback', {})  # Example: {"docno1": 1, "docno2": 0}

    if not query:
        return Response({"error": "Query parameter is required"}, status=400)

    try:
        # Step 1: Update global feedback store
        if query not in feedback_store:
            feedback_store[query] = {}
        feedback_store[query].update(feedback)

        # Step 2: Retrieve all stored feedback for the query
        stored_feedback = feedback_store.get(query, {})
        relevant_docs = [doc for doc, rel in stored_feedback.items() if rel == "relevant"]
        non_relevant_docs = [doc for doc, rel in stored_feedback.items() if rel == "irrelevant"]

        # Step 3: Perform the search
        results = retriever.search(query)

        # Step 4: Boost relevant and penalize irrelevant docs
        if stored_feedback:
            results["score"] = results["score"] * results["docno"].apply(
                lambda doc: 1.5 if doc in relevant_docs else (0.5 if doc in non_relevant_docs else 1.0)
            )

            # Re-sort by updated scores
            results = results.sort_values(by="score", ascending=False)

        # Step 5: Format the response
        data = results[['docno', 'raw_title', 'raw_text', 'score', 'link']].to_dict(orient='records')
        return Response(data)

    except Exception as e:
        return Response({"error": f"Internal Server Error: {str(e)}"}, status=500)
