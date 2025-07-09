#!/usr/bin/env python3
"""
Migrate Blogspot content to Jekyll
"""

import os
import re
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import html2text
import time
import sys

class BlogspotMigrator:
    def __init__(self):
        self.base_url = "https://windleblo.blogspot.com"
        self.sitemap_url = "https://windleblo.blogspot.com/sitemap.xml"
        self.posts_dir = Path("_posts")
        self.assets_dir = Path("assets/images/blogspot")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Create directories
        self.posts_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        # HTML to Markdown converter
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0
        
    def get_sitemap_urls(self):
        """Extract all blog post URLs from sitemap"""
        print("Fetching sitemap...")
        
        try:
            response = self.session.get(self.sitemap_url)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            urls = []
            
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None:
                    url_text = loc.text
                    # Only include actual blog post URLs (not feeds, pages, etc.)
                    if '/201' in url_text and url_text.endswith('.html'):
                        urls.append(url_text)
            
            print(f"Found {len(urls)} blog post URLs")
            return sorted(urls)
            
        except Exception as e:
            print(f"Error fetching sitemap: {e}")
            return []
    
    def extract_post_date(self, url):
        """Extract date from URL pattern"""
        match = re.search(r'/(\d{4})/(\d{2})/', url)
        if match:
            year, month = match.groups()
            return f"{year}-{month}-01"  # Default to 1st of month
        return None
    
    def extract_post_slug(self, url):
        """Extract slug from URL"""
        return url.split('/')[-1].replace('.html', '')
    
    def fetch_post_content(self, url):
        """Fetch and parse individual post content"""
        print(f"Fetching: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Basic HTML parsing to extract post content
            html_content = response.text
            
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL)
            title = title_match.group(1).strip() if title_match else "Untitled"
            
            # Remove " - Windleblo" suffix if present
            title = re.sub(r'\s*-\s*Windleblo\s*$', '', title)
            
            # Extract post content (this is a simplified approach)
            # Look for the main post content div
            content_patterns = [
                r'<div class="post-body[^"]*"[^>]*>(.*?)</div>',
                r'<div class="entry-content[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*post-body[^"]*"[^>]*>(.*?)</div>'
            ]
            
            content = ""
            for pattern in content_patterns:
                match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1)
                    break
            
            if not content:
                print(f"Warning: Could not extract content from {url}")
                return None
            
            return {
                'title': title,
                'content': content,
                'url': url
            }
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def convert_to_markdown(self, html_content):
        """Convert HTML content to Markdown"""
        try:
            # Clean up HTML before conversion
            html_content = re.sub(r'<br\s*/?>', '\n', html_content)
            html_content = re.sub(r'<div[^>]*>', '\n', html_content)
            html_content = re.sub(r'</div>', '\n', html_content)
            
            # Convert to markdown
            markdown = self.h2t.handle(html_content)
            
            # Clean up markdown
            markdown = re.sub(r'\n{3,}', '\n\n', markdown)
            markdown = markdown.strip()
            
            return markdown
            
        except Exception as e:
            print(f"Error converting to markdown: {e}")
            return html_content
    
    def create_jekyll_post(self, post_data, post_date):
        """Create Jekyll post file"""
        try:
            # Parse date
            date_obj = datetime.strptime(post_date, '%Y-%m-%d')
            
            # Create filename
            slug = self.extract_post_slug(post_data['url'])
            filename = f"{post_date}-{slug}.md"
            filepath = self.posts_dir / filename
            
            # Convert content to markdown
            markdown_content = self.convert_to_markdown(post_data['content'])
            
            # Create Jekyll frontmatter
            frontmatter = f"""---
layout: post
title: "{post_data['title']}"
date: {date_obj.strftime('%Y-%m-%d')}T12:00:00-07:00
author: Jack
categories: [uncategorized]
original_url: {post_data['url']}
---

{markdown_content}"""
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
            
            print(f"Created: {filename}")
            return True
            
        except Exception as e:
            print(f"Error creating Jekyll post: {e}")
            return False
    
    def migrate_all_posts(self):
        """Main migration function"""
        print("Starting Blogspot migration...")
        
        # Get all post URLs
        urls = self.get_sitemap_urls()
        
        if not urls:
            print("No URLs found to migrate")
            return
        
        print(f"Starting migration of {len(urls)} posts...")
        
        successful = 0
        failed = 0
        
        for url in urls:
            # Extract date from URL
            post_date = self.extract_post_date(url)
            if not post_date:
                print(f"Could not extract date from {url}")
                failed += 1
                continue
            
            # Fetch post content
            post_data = self.fetch_post_content(url)
            if not post_data:
                failed += 1
                continue
            
            # Create Jekyll post
            if self.create_jekyll_post(post_data, post_date):
                successful += 1
            else:
                failed += 1
            
            # Be nice to the server
            time.sleep(1)
        
        print(f"Migration complete: {successful} successful, {failed} failed")

if __name__ == "__main__":
    migrator = BlogspotMigrator()
    migrator.migrate_all_posts()