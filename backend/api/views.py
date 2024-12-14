from rest_framework.decorators import api_view
from rest_framework.response import Response
import pyterrier as pt
import os
from django.conf import settings

if not pt.java.started():
    pt.java.init()

index_path = os.path.join(settings.BASE_DIR, "..", "pyTerrier", "ikea_index")
index = pt.IndexFactory.of(index_path)

retriever = pt.BatchRetrieve(index, num_results=5, metadata=["docno", "title", "text", "raw_title", "raw_text"])

@api_view(['GET'])
def search_view(request):
    query = request.GET.get('query', '')  # Example: /api/search?query=ikea
    if not query:
        return Response({"error": "Query parameter is required"}, status=400)
    
    results = retriever.search(query)
    
    data = results[['docno', 'raw_title', 'raw_text', 'score']].to_dict(orient='records')
    
    return Response(data)
