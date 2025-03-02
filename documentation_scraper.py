# documentation_scraper.py
import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin
import logging

class CDPDocumentationScraper:
    def __init__(self, base_url, name):
        self.base_url = base_url
        self.name = name
        self.visited_urls = set()
        self.docs_data = []
        self.logger = logging.getLogger(__name__)

    def scrape_documentation(self, max_pages=500):
        """Scrape documentation pages starting from the base URL"""
        self.logger.info(f"Starting scraping for {self.name} at {self.base_url}")
        self._crawl_page(self.base_url, max_pages)
        self.logger.info(f"Finished scraping for {self.name}. Found {len(self.docs_data)} documents.")
        return self.docs_data
        
    def _crawl_page(self, url, max_pages):
        """Recursively crawl pages within the documentation"""
        if url in self.visited_urls or len(self.visited_urls) >= max_pages:
            return
            
        self.visited_urls.add(url)
        self.logger.debug(f"Crawling {url}")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                return
                
            soup = BeautifulSoup(response.text, 'html.parser')
            self.logger.debug(f"Successfully parsed {url}")
            
            # Extract content from typical documentation structure
            content_div = soup.find('div', class_=['documentation-content', 'docs-content', 'main-content'])
            if not content_div:
                content_div = soup.find('article') or soup.find('main')
                
            if content_div:
                # Extract title
                title = soup.find('h1')
                title_text = title.get_text().strip() if title else "Untitled"
                
                # Extract content sections
                sections = []
                current_section = {"title": None, "content": []}
                
                for element in content_div.find_all(['h2', 'h3', 'p', 'pre', 'ul', 'ol']):
                    if element.name in ['h2', 'h3']:
                        if current_section["content"]:
                            sections.append(current_section)
                        current_section = {"title": element.get_text().strip(), "content": []}
                    else:
                        current_section["content"].append(str(element))
                
                if current_section["content"]:
                    sections.append(current_section)
                
                # Store the processed document
                doc_data = {
                    "platform": self.name,
                    "url": url,
                    "title": title_text,
                    "sections": sections,
                    "full_text": content_div.get_text(),
                }
                self.docs_data.append(doc_data)
            
            # Find links to other documentation pages
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('#') or href.startswith('mailto:'):
                    continue
                    
                full_url = urljoin(url, href)
                # Only follow links within the documentation domain
                if self.base_url in full_url and full_url not in self.visited_urls:
                    self._crawl_page(full_url, max_pages)
                    
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {e}")
            print(f"Error crawling {url}: {e}")

# Example usage
if __name__ == "_main_":
    cdps = [
        {"name": "segment", "url": "https://segment.com/docs/?ref=nav"},
        {"name": "mparticle", "url": "https://docs.mparticle.com/"},
        {"name": "lytics", "url": "https://docs.lytics.com/"},
        {"name": "zeotap", "url": "https://docs.zeotap.com/home/en-us/"}
    ]
    
    for cdp in cdps:
        scraper = CDPDocumentationScraper(cdp["url"], cdp["name"])
        data = scraper.scrape_documentation()
        
        # Save to JSON file
        with open(f"{cdp['name']}_docs.json", 'w') as f:
            json.dump(data, f, indent=2)