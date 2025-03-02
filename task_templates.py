# task_templates.py
class TaskTemplates:
    def __init__(self):
        self.templates = {
            "source_setup": {
                "title": "Setting up a new Source in {platform}",
                "intro": "To set up a new source in {platform}, follow these steps:",
                "outro": "After completing these steps, your source will be ready to collect data."
            },
            "audience_creation": {
                "title": "Creating an Audience in {platform}",
                "intro": "To create an audience in {platform}, you'll need to:",
                "outro": "Your audience is now ready to be used across your integrations."
            },
            "integration_connection": {
                "title": "Connecting {integration} with {platform}",
                "intro": "To integrate {integration} with {platform}, follow this process:",
                "outro": "Your {integration} integration is now set up and ready to use with {platform}."
            },
            "data_mapping": {
                "title": "Mapping Data in {platform}",
                "intro": "To map your data fields in {platform}:",
                "outro": "Your data mapping is now complete and will be applied to incoming data."
            }
        }
    
    def get_template(self, task_type, **kwargs):
        """Get a template for a specific task type with formatted fields"""
        if task_type not in self.templates:
            return None
        
        template = self.templates[task_type]
        
        # Format each field with provided kwargs
        formatted_template = {}
        for key, value in template.items():
            formatted_template[key] = value.format(**kwargs)
        
        return formatted_template
    
    def detect_task_type(self, query, key_terms):
        """Detect the task type from a query"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["source", "add source", "create source", "set up source"]):
            return "source_setup"
        
        if any(term in query_lower for term in ["audience", "segment", "user group"]):
            return "audience_creation"
        
        if any(term in query_lower for term in ["connect", "integration", "integrate"]):
            # Try to identify the integration
            integration = None
            common_integrations = ["google", "facebook", "amplitude", "mixpanel", "salesforce"]
            for intg in common_integrations:
                if intg in query_lower:
                    integration = intg.capitalize()
                    break
            
            return "integration_connection", {"integration": integration or "the service"}
        
        if any(term in query_lower for term in ["map", "mapping", "transform", "field"]):
            return "data_mapping"
        
        return None