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
import hashlib
import mimetypes

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
        
        # Track downloaded images and redirects
        self.downloaded_images = {}  # URL -> local path mapping
        self.redirects = []  # List of (old_url, new_url) tuples
        
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
    
    def extract_better_date(self, html_content, fallback_date):
        """Try to extract a more specific date from the post HTML"""
        # Look for published date in meta tags or structured data
        patterns = [
            r'<meta[^>]*property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)["\']',
            r'<time[^>]*datetime=["\']([^"\']+)["\']',
            r'<abbr[^>]*class=["\']published["\'][^>]*title=["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Try to parse the date
                    if 'T' in date_str:
                        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
        
        return fallback_date
    
    def extract_post_slug(self, url):
        """Extract slug from URL"""
        return url.split('/')[-1].replace('.html', '')
    
    def download_image(self, img_url, post_date):
        """Download image and return local path"""
        try:
            # Skip if already downloaded
            if img_url in self.downloaded_images:
                return self.downloaded_images[img_url]
            
            print(f"  Downloading image: {img_url}")
            
            # Create year-based directory
            year = post_date.split('-')[0]
            year_dir = self.assets_dir / year
            year_dir.mkdir(exist_ok=True)
            
            # Download image
            response = self.session.get(img_url, timeout=30)
            response.raise_for_status()
            
            # Get content type and extension
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                print(f"    Warning: Not an image content type: {content_type}")
                return None
            
            # Generate filename
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            extension = mimetypes.guess_extension(content_type) or '.jpg'
            filename = f"img_{url_hash}{extension}"
            
            # Save image
            local_path = year_dir / filename
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            # Return path relative to site root
            relative_path = f"/assets/images/blogspot/{year}/{filename}"
            self.downloaded_images[img_url] = relative_path
            
            print(f"    Saved: {relative_path}")
            return relative_path
            
        except Exception as e:
            print(f"    Error downloading {img_url}: {e}")
            return None
    
    def process_images_in_content(self, content, post_date):
        """Find and download images in content, update URLs"""
        # Find all image tags
        img_pattern = r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>'
        images = re.findall(img_pattern, content, re.IGNORECASE)
        
        if not images:
            return content
        
        print(f"  Found {len(images)} images to process")
        
        for img_url in images:
            # Skip data URLs and relative URLs
            if img_url.startswith('data:') or not img_url.startswith('http'):
                continue
            
            # Download image
            local_path = self.download_image(img_url, post_date)
            
            if local_path:
                # Replace URL in content
                content = content.replace(img_url, local_path)
        
        return content
    
    def update_internal_links(self, content, post_date):
        """Update links to other Blogspot posts"""
        # Pattern to match links to windleblo.blogspot.com posts
        link_pattern = r'https?://windleblo\.blogspot\.com/(\d{4})/(\d{2})/([^/]+)\.html'
        
        def replace_link(match):
            year, month, slug = match.groups()
            # Convert to Jekyll URL format
            new_url = f"/blog/{year}/{month}/01/{slug}/"
            return new_url
        
        updated_content = re.sub(link_pattern, replace_link, content)
        return updated_content
    
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
            # Remove "Windleblo: " prefix if present
            title = re.sub(r'^Windleblo:\s*', '', title)
            
            # Extract post content - look for Blogspot-specific patterns
            content_patterns = [
                r'<div[^>]*class=["\']post-body entry-content["\'][^>]*>(.*?)</div>',
                r'<div[^>]*itemprop=["\']description articleBody["\'][^>]*>(.*?)</div>',
                r'<div[^>]*class=["\']post-body["\'][^>]*>(.*?)</div>',
                r'<div[^>]*class=["\']entry-content["\'][^>]*>(.*?)</div>'
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
                'url': url,
                'html_content': html_content,
                'raw_content': content  # Keep original for processing
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
            
            # Process images and internal links
            content = post_data['raw_content']
            
            # First, process images from the full HTML (they might be outside the post body)
            # but only to download them - we'll replace URLs in the content
            full_html = post_data['html_content']
            self.process_images_in_content(full_html, post_date)
            
            # Now process the extracted content for any images and replace URLs
            content = self.process_images_in_content(content, post_date)
            
            # Update internal links
            content = self.update_internal_links(content, post_date)
            
            # Convert content to markdown
            markdown_content = self.convert_to_markdown(content)
            
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
            
            # Track redirect
            jekyll_url = f"/blog/{date_obj.strftime('%Y/%m/%d')}/{slug}/"
            self.redirects.append((post_data['url'], jekyll_url))
            
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
            
            # Try to get better date from post content
            better_date = self.extract_better_date(post_data.get('html_content', ''), post_date)
            
            # Create Jekyll post
            if self.create_jekyll_post(post_data, better_date):
                successful += 1
            else:
                failed += 1
            
            # Be nice to the server
            time.sleep(1)
        
        print(f"Migration complete: {successful} successful, {failed} failed")
        
        # Generate redirect file
        self.generate_redirects()
        
        print(f"Downloaded {len(self.downloaded_images)} images")
        print(f"Generated {len(self.redirects)} redirects")
    
    def generate_redirects(self):
        """Generate Netlify redirects file"""
        if not self.redirects:
            return
        
        redirects_file = Path("_redirects")
        
        print("Generating redirects file...")
        
        with open(redirects_file, 'w') as f:
            f.write("# Blogspot to Jekyll redirects\n")
            f.write("# Generated by migrate_blogspot.py\n\n")
            
            for old_url, new_url in self.redirects:
                # Convert full URL to path
                old_path = old_url.replace('https://windleblo.blogspot.com', '')
                f.write(f"{old_path} {new_url} 301\n")
        
        print(f"Created {redirects_file} with {len(self.redirects)} redirects")

if __name__ == "__main__":
    migrator = BlogspotMigrator()
    migrator.migrate_all_posts()