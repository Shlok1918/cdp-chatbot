# main.py
import argparse
import os
import logging
from query_processor import QueryProcessor
from document_indexer import DocumentIndexer
from response_generator import ResponseGenerator
from documentation_scraper import CDPDocumentationScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scrape_documentation():
    """Scrape documentation from all CDPs"""
    logger.info("Starting documentation scraping process...")
    
    cdps = [
        {"name": "segment", "url": "https://segment.com/docs/"},
        {"name": "mparticle", "url": "https://docs.mparticle.com/"},
        {"name": "lytics", "url": "https://docs.lytics.com/"},
        {"name": "zeotap", "url": "https://docs.zeotap.com/home/en-us/"}
    ]
    
    for cdp in cdps:
        logger.info(f"Scraping documentation for {cdp['name']}...")
        scraper = CDPDocumentationScraper(cdp["url"], cdp["name"])
        data = scraper.scrape_documentation()
        
        # Save to JSON file
        output_file = f"{cdp['name']}_docs.json"
        with open(output_file, 'w') as f:
            import json
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(data)} documents to {output_file}")
    
    logger.info("Documentation scraping completed.")

def build_index():
    """Build the document index"""
    logger.info("Building document index...")
    
    indexer = DocumentIndexer()
    
    input_files = [
        "segment_docs.json", 
        "mparticle_docs.json", 
        "lytics_docs.json", 
        "zeotap_docs.json"
    ]
    
    # Check if all files exist
    missing_files = [f for f in input_files if not os.path.exists(f)]
    if missing_files:
        logger.error(f"Missing documentation files: {missing_files}")
        logger.info("Please run scraping first with: python main.py --scrape")
        return False
    
    indexer.load_documents(input_files)
    indexer.save_index()
    
    logger.info(f"Index built with {len(indexer.documents)} documents")
    return True

def start_server():
    """Start the web server"""
    logger.info("Starting web server...")
    from app import app
    app.run(host='0.0.0.0', port=5000)

def main():
    parser = argparse.ArgumentParser(description='CDP Chatbot Manager')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--scrape', action='store_true', help='Scrape CDP documentation')
    group.add_argument('--build-index', action='store_true', help='Build document index')
    group.add_argument('--server', action='store_true', help='Start the web server')
    
    args = parser.parse_args()
    
    if args.scrape:
        scrape_documentation()
    elif args.build_index:
        build_index()
    elif args.server:
        if not os.path.exists("cdp_docs_index.pkl"):
            logger.warning("Index file not found. Building index first...")
            if build_index():
                start_server()
        else:
            start_server()
    else:
        # Default: check environment and run appropriate steps
        if not os.path.exists("segment_docs.json"):
            logger.info("Documentation files not found. Running scraping process...")
            scrape_documentation()
        
        if not os.path.exists("cdp_docs_index.pkl"):
            logger.info("Index not found. Building index...")
            build_index()
        
        logger.info("Starting web server...")
        start_server()

if __name__ == "__main__":
    main()