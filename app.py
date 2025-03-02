# app.py
from flask import Flask, request, jsonify, render_template
from query_processor import QueryProcessor
from document_indexer import DocumentIndexer
from response_generator import ResponseGenerator

app = Flask(__name__)

# Initialize components
query_processor = QueryProcessor()
document_indexer = DocumentIndexer()
document_indexer.load_index("cdp_docs_index.pkl")
response_generator = ResponseGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    # Process the query
    query_info = query_processor.process_query(query)
    
    # Search for relevant documentation
    if query_info["platforms"]:
        # If specific platform(s) mentioned, search within those platforms
        all_results = []
        for platform in query_info["platforms"]:
            platform_results = document_indexer.search(
                query_info["enhanced_query"], 
                platform=platform,
                top_k=3
            )
            all_results.extend(platform_results)
            
        # Sort by relevance score
        search_results = sorted(all_results, key=lambda x: x["score"], reverse=True)[:5]
    else:
        # Search across all platforms
        search_results = document_indexer.search(
            query_info["enhanced_query"], 
            top_k=5
        )
    
    # Generate response
    response_text = response_generator.generate_response(query_info, search_results)
    
    # Return results
    return jsonify({
        "query": query,
        "response": response_text,
        "sources": [
            {
                "platform": result["document"]["platform"],
                "title": result["document"]["page_title"],
                "url": result["document"]["url"],
                "relevance": result["score"]
            }
            for result in search_results
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)