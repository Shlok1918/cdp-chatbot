# query_processor.py
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class QueryProcessor:
    def __init__(self):
        # Download NLTK resources if not already downloaded
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        
        # CDP platform names and aliases
        self.cdp_platforms = {
            "segment": ["segment", "segment.com", "segment.io"],
            "mparticle": ["mparticle", "m-particle", "m particle"],
            "lytics": ["lytics", "lytics.io"],
            "zeotap": ["zeotap", "zeotap.com"]
        }
        
        # Define patterns for how-to questions
        self.how_to_patterns = [
            r"how (do|can|should|would) (i|we|you)",
            r"how to",
            r"steps (for|to)",
            r"guide (for|to)",
            r"process (of|for)",
            r"(create|setup|configure|implement|integrate|use)",
            r"way to",
            r"method (of|for)"
        ]
    
    def process_query(self, query):
        """Process and classify the user query"""
        # Lowercase the query
        query = query.lower()
        
        # Check if this is a how-to question
        is_how_to = self._is_how_to_question(query)
        
        # Identify which platform(s) the query is about
        platforms = self._identify_platforms(query)
        
        # Extract key terms
        key_terms = self._extract_key_terms(query)
        
        return {
            "original_query": query,
            "is_how_to": is_how_to,
            "platforms": platforms,
            "key_terms": key_terms,
            "is_comparison": len(platforms) > 1 or "compare" in query or "comparison" in query,
            "enhanced_query": self._enhance_query(query, is_how_to, platforms, key_terms)
        }
    
    def _is_how_to_question(self, query):
        """Check if the query is a how-to question"""
        for pattern in self.how_to_patterns:
            if re.search(pattern, query):
                return True
        return False
    
    def _identify_platforms(self, query):
        """Identify which CDP platforms are mentioned in the query"""
        mentioned_platforms = []
        
        for platform, aliases in self.cdp_platforms.items():
            for alias in aliases:
                if alias in query or alias.replace(" ", "") in query:
                    mentioned_platforms.append(platform)
                    break
        
        return mentioned_platforms
    
    def _extract_key_terms(self, query):
        """Extract key terms from the query"""
        # Tokenize and filter stop words
        tokens = word_tokenize(query)
        filtered_tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]
        
        # Add specific CDP feature terms that might be important
        cdp_terms = ["source", "destination", "integration", "identity", "profile", "audience", 
                     "segment", "track", "event", "identify", "user", "data", "pipeline",
                     "transform", "webhook", "api", "sdk", "stream", "batch"]
        
        key_terms = []
        for term in filtered_tokens:
            if term in cdp_terms or len(term) > 3:  # Keep longer words and specific terms
                key_terms.append(term)
        
        return key_terms
    
    def _enhance_query(self, query, is_how_to, platforms, key_terms):
        """Create an enhanced query for better search results"""
        enhanced_parts = []
        
        # Add how-to context if needed
        if is_how_to and not any(re.search(pattern, query) for pattern in self.how_to_patterns):
            enhanced_parts.append("how to")
        
        # Add platform if only one is identified but not explicitly mentioned
        if len(platforms) == 1 and not any(platform in query for platform in platforms):
            enhanced_parts.append(platforms[0])
        
        # Add the original query
        enhanced_parts.append(query)
        
        # Add any key CDP-specific terms that might be implied but not stated
        if "create" in query or "new" in query:
            if "source" not in query and "destination" not in query and "integration" not in query:
                enhanced_parts.append("source destination integration")
        
        if "user" in query or "profile" in query:
            if "identity" not in query:
                enhanced_parts.append("identity")
        
        if "audience" in query or "segment" in query:
            if "create" not in query:
                enhanced_parts.append("create audience")
        
        return " ".join(enhanced_parts)

# Example usage
if __name__ == "_main_":
    processor = QueryProcessor()
    
    test_queries = [
        "How do I set up a new source in Segment?",
        "Create a user profile in mParticle",
        "Lytics audience creation process",
        "How does Segment's audience creation compare to Lytics?",
        "Integrate Google Analytics with Zeotap"
    ]
    
    for query in test_queries:
        result = processor.process_query(query)
        print(f"Query: {query}")
        print(f"Is How-To: {result['is_how_to']}")
        print(f"Platforms: {result['platforms']}")
        print(f"Key Terms: {result['key_terms']}")
        print(f"Is Comparison: {result['is_comparison']}")
        print(f"Enhanced Query: {result['enhanced_query']}")
        print("-" * 50)