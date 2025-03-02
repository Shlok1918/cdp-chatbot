# response_generator.py
import re
from html import escape

class ResponseGenerator:
    def __init__(self):
        pass
    
    def generate_response(self, query_info, search_results):
        """Generate a response to the user query based on search results"""
        if not search_results:
            return self._generate_fallback_response(query_info)
        
        # Determine response type based on query info
        if query_info["is_comparison"]:
            return self._generate_comparison_response(query_info, search_results)
        else:
            return self._generate_how_to_response(query_info, search_results)
    
    def _generate_how_to_response(self, query_info, search_results):
        """Generate step-by-step how-to response"""
        platform = query_info["platforms"][0] if query_info["platforms"] else None
        top_result = search_results[0]["document"]
        
        platform_name = top_result["platform"].capitalize()
        page_title = top_result["page_title"]
        section_title = top_result["section_title"] or "How to"
        url = top_result["url"]
        
        content = top_result["content"]
        
        # Clean and format the content
        content = self._clean_html(content)
        
        # Extract steps or instructions
        steps = self._extract_steps(content)
        
        if steps:
            instructions = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        else:
            # If no clear steps, use the content directly
            instructions = content
        
        # Generate the response
        response = f"# How to {page_title} in {platform_name}\n\n"
        response += f"## {section_title}\n\n"
        response += instructions
        
        # Add source reference
        response += f"\n\nFor more detailed information, you can check the [{platform_name} documentation]({url})."
        
        return response
    
    def _generate_comparison_response(self, query_info, search_results):
        """Generate a comparison between platforms"""
        platforms = query_info["platforms"]
        
        if len(platforms) < 2:
            # If only one platform was explicitly mentioned but it's a comparison query
            mentioned_platform = platforms[0] if platforms else None
            platforms = [p for p in ["segment", "mparticle", "lytics", "zeotap"] if p != mentioned_platform][:2]
            if mentioned_platform:
                platforms.insert(0, mentioned_platform)
        
        # Group results by platform
        platform_results = {}
        for platform in platforms:
            platform_results[platform] = [r for r in search_results if r["document"]["platform"] == platform]
        
        # Build the comparison response
        response = f"# Comparison: {', '.join(p.capitalize() for p in platforms)}\n\n"
        
        # Extract the key feature being compared
        feature = " ".join(query_info["key_terms"][:3]) or "this feature"
        
        response += f"Here's how {feature} compares across the platforms:\n\n"
        
        for platform in platforms:
            response += f"## {platform.capitalize()}\n\n"
            
            if platform_results[platform]:
                top_result = platform_results[platform][0]["document"]
                content = self._clean_html(top_result["content"])
                response += f"{content[:400]}...\n\n"
                response += f"[Learn more about {platform.capitalize()} {feature}]({top_result['url']})\n\n"
            else:
                response += f"No specific information found for {platform}. You may want to check their documentation directly.\n\n"
        
        return response
    
    def _generate_fallback_response(self, query_info):
        """Generate a fallback response when no relevant results are found"""
        if query_info["platforms"]:
            platform = query_info["platforms"][0].capitalize()
            return (f"I couldn't find specific information about this in the {platform} documentation. "
                    f"You might want to check the official {platform} documentation directly "
                    f"or try rephrasing your question.")
        else:
            return ("I couldn't find specific information about this in the CDP documentation. "
                    "Please specify which CDP platform you're interested in (Segment, mParticle, Lytics, or Zeotap) "
                    "or try rephrasing your question.")
    
    def _clean_html(self, content):
        """Clean HTML content for display"""
        # Remove HTML tags
        clean_text = re.sub(r'<.*?>', ' ', content)
        # Fix spacing
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    
    def _extract_steps(self, content):
        """Try to extract sequential steps from content"""
        # Look for numbered steps
        numbered_steps = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|$)', content)
        if numbered_steps and len(numbered_steps) > 1:
            return numbered_steps
        
        # Look for bullet points
        bullet_steps = re.findall(r'[•-]\s+(.?)(?=[•*-]|$)', content)
        if bullet_steps and len(bullet_steps) > 1:
            return bullet_steps
        
        # Look for sentences that might be steps
        sentences = re.split(r'(?<=[.!?])\s+', content)
        action_sentences = [s for s in sentences if re.search(r'^(Click|Select|Enter|Type|Go to|Navigate|Choose|Configure|Set|Create)', s)]
        
        if action_sentences and len(action_sentences) > 1:
            return action_sentences
        
        return None

# Example usage
if __name__ == "_main_":
    generator = ResponseGenerator()
    
    query_info = {
        "original_query": "How do I set up a new source in Segment?",
        "is_how_to": True,
        "platforms": ["segment"],
        "key_terms": ["setup", "source", "segment"],
        "is_comparison": False
    }
    
    mock_result = {
        "document": {
            "platform": "segment",
            "url": "https://segment.com/docs/connections/sources/",
            "page_title": "Setting up a Source",
            "section_title": "Creating a New Source",
            "content": "1. Log in to your Segment workspace. 2. Navigate to Connections > Sources. 3. Click Add Source. 4. Select the type of source you want to create. 5. Name your source and click Add Source."
        },
        "score": 0.85
    }
    
    response = generator.generate_response(query_info, [mock_result])
    print(response)