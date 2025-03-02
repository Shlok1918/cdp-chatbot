# comparison_handler.py
class ComparisonHandler:
    def __init__(self, indexer):
        self.indexer = indexer
        self.feature_mapping = {
            "audience": ["audience", "segment", "user group", "cohort"],
            "identity": ["identity", "user profile", "customer profile", "identification"],
            "tracking": ["track", "event", "analytics", "behavior"],
            "integration": ["integration", "connection", "source", "destination"],
            "data governance": ["governance", "privacy", "consent", "regulation", "gdpr", "ccpa"],
            "transformation": ["transform", "mapping", "filter", "enrich"]
        }
    
    def get_comparison_data(self, feature, platforms=None):
        """Get comparison data for a specific feature across platforms"""
        if platforms is None or len(platforms) == 0:
            platforms = ["segment", "mparticle", "lytics", "zeotap"]
        
        # Identify the feature category
        feature_category = self._identify_feature_category(feature)
        
        # Create search terms for each platform
        comparison_data = {}
        
        for platform in platforms:
            search_query = f"{platform} {feature_category} {feature}"
            results = self.indexer.search(search_query, platform=platform, top_k=3)
            
            if results:
                best_result = results[0]["document"]
                comparison_data[platform] = {
                    "title": best_result["section_title"] or best_result["page_title"],
                    "content": best_result["content"],
                    "url": best_result["url"]
                }
            else:
                comparison_data[platform] = {
                    "title": f"No information about {feature} in {platform}",
                    "content": "",
                    "url": ""
                }
        
        return feature_category, comparison_data
    
    def _identify_feature_category(self, feature):
        """Map a specific feature to a general category"""
        for category, terms in self.feature_mapping.items():
            if any(term in feature.lower() for term in terms):
                return category
        return "general feature"