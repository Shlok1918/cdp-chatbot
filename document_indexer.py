# document_indexer.py
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

class DocumentIndexer:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
        
    def load_documents(self, filenames):
        """Load documents from multiple JSON files"""
        for filename in filenames:
            with open(filename, 'r') as f:
                platform_docs = json.load(f)
                
            # Process each document
            for doc in platform_docs:
                # Create chunked documents for each section
                for section in doc["sections"]:
                    section_doc = {
                        "platform": doc["platform"],
                        "url": doc["url"],
                        "page_title": doc["title"],
                        "section_title": section["title"],
                        "content": " ".join(section["content"]),
                        "id": f"{doc['platform']}_{len(self.documents)}"
                    }
                    self.documents.append(section_doc)
        
        # Create document embeddings
        self._create_embeddings()
        
    def _create_embeddings(self):
        """Create embeddings for all documents"""
        texts = []
        for doc in self.documents:
            # Create a rich representation for embedding
            text = f"{doc['platform']} {doc['page_title']} {doc['section_title']} {doc['content']}"
            texts.append(text)
            
        self.embeddings = self.model.encode(texts)
        
    def save_index(self, filename="cdp_docs_index.pkl"):
        """Save the index to disk"""
        with open(filename, 'wb') as f:
            pickle.dump({
                "documents": self.documents,
                "embeddings": self.embeddings
            }, f)
            
    def load_index(self, filename="cdp_docs_index.pkl"):
        """Load the index from disk"""
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            self.documents = data["documents"]
            self.embeddings = data["embeddings"]
    
    def search(self, query, platform=None, top_k=5):
        """Search for relevant documents"""
        query_embedding = self.model.encode([query])[0]
        
        # Calculate similarity scores
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        
        # Get top results
        if platform:
            # Filter by platform if specified
            platform_indices = [i for i, doc in enumerate(self.documents) 
                              if doc["platform"].lower() == platform.lower()]
            platform_similarities = [(i, similarities[i]) for i in platform_indices]
            top_indices = sorted(platform_similarities, key=lambda x: x[1], reverse=True)[:top_k]
        else:
            top_indices = sorted(enumerate(similarities), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for idx, score in top_indices:
            if score < 0.3:  # Similarity threshold
                continue
            results.append({
                "document": self.documents[idx],
                "score": float(score)
            })
            
        return results

# Example usage
if __name__ == "_main_":
    indexer = DocumentIndexer()
    indexer.load_documents([
        "segment_docs.json", 
        "mparticle_docs.json", 
        "lytics_docs.json", 
        "zeotap_docs.json"
    ])
    indexer.save_index()
    
    # Test search
    results = indexer.search("How to set up a new source in Segment")
    for result in results:
        print(f"Score: {result['score']:.4f}")
        print(f"Platform: {result['document']['platform']}")
        print(f"Title: {result['document']['page_title']} - {result['document']['section_title']}")
        print(f"URL: {result['document']['url']}")
        print("-" * 50)