#!/usr/bin/env python3
"""
Extract blog content from Wayback Machine HTML archives
"""

import os
import re
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser
from html import unescape

class ContentExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_content = False
        self.in_date = False
        self.title = ""
        self.content = []
        self.date = ""
        self.current_tag = []
        
    def handle_starttag(self, tag, attrs):
        self.current_tag.append(tag)
        attrs_dict = dict(attrs)
        
        # Look for title
        if tag == 'h1' and 'entry-title' in attrs_dict.get('class', ''):
            self.in_title = True
            
        # Look for content
        if 'entry-content' in attrs_dict.get('class', ''):
            self.in_content = True
            
        # Look for date
        if tag == 'time' and 'entry-date' in attrs_dict.get('class', ''):
            self.date = attrs_dict.get('datetime', '')
            
        # Handle content tags
        if self.in_content:
            if tag == 'p':
                self.content.append('\n')
            elif tag in ['h2', 'h3', 'h4', 'h5', 'h6']:
                self.content.append(f'\n{"#" * int(tag[1])} ')
            elif tag == 'img':
                src = attrs_dict.get('src', '')
                alt = attrs_dict.get('alt', '')
                # Clean wayback machine URLs
                src = re.sub(r'https://web\.archive\.org/web/\d+im_/', '', src)
                if src:
                    self.content.append(f'\n![{alt}]({src})\n')
            elif tag == 'a' and self.current_tag[-2] != 'nav':
                href = attrs_dict.get('href', '')
                # Clean wayback machine URLs
                href = re.sub(r'https://web\.archive\.org/web/\d+/', '', href)
                self.content.append(f'[')
    
    def handle_endtag(self, tag):
        if self.current_tag and self.current_tag[-1] == tag:
            self.current_tag.pop()
            
        if tag == 'h1' and self.in_title:
            self.in_title = False
            
        if self.in_content and 'entry-content' in ' '.join(self.current_tag):
            if tag == 'div':
                self.in_content = False
            elif tag == 'p':
                self.content.append('\n')
            elif tag == 'a':
                # Find the matching opening bracket
                text = ''.join(self.content)
                if text.rfind('[') != -1:
                    self.content.append(']')
                    # Add href after the bracket
                    
    def handle_data(self, data):
        if self.in_title:
            self.title += data.strip()
            
        if self.in_content:
            # Skip wayback machine injected content
            if 'FILE ARCHIVED ON' not in data and 'INTERNET ARCHIVE' not in data:
                cleaned = data.strip()
                if cleaned:
                    self.content.append(cleaned + ' ')


def extract_post(html_file):
    """Extract post data from HTML file"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Remove wayback machine wrapper
    html_content = re.sub(r'<!--\s*BEGIN WAYBACK TOOLBAR.*?END WAYBACK TOOLBAR\s*-->', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
    
    parser = ContentExtractor()
    parser.feed(html_content)
    
    # Clean up content
    content_text = ''.join(parser.content).strip()
    content_text = re.sub(r'\n{3,}', '\n\n', content_text)  # Remove excessive newlines
    content_text = re.sub(r' +', ' ', content_text)  # Remove multiple spaces
    
    # Extract date from file path if not found in HTML
    if not parser.date:
        match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', str(html_file))
        if match:
            parser.date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    
    # Extract slug from file path
    slug = Path(html_file).stem
    
    return {
        'title': parser.title or slug.replace('-', ' ').title(),
        'date': parser.date,
        'slug': slug,
        'content': content_text
    }


def create_jekyll_post(post_data, output_dir):
    """Create Jekyll post file"""
    if not post_data['date']:
        return False
        
    # Format filename
    date_obj = datetime.fromisoformat(post_data['date'].split('T')[0])
    filename = f"{date_obj.strftime('%Y-%m-%d')}-{post_data['slug']}.md"
    filepath = Path(output_dir) / filename
    
    # Create front matter
    front_matter = f"""---
layout: post
title: "{post_data['title']}"
date: {post_data['date']}
author: Jack
categories: [uncategorized]
---

"""
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(front_matter)
        f.write(post_data['content'])
    
    print(f"Created: {filename}")
    return True


def main():
    archive_dir = Path("/Users/x25bd/Code/windleblo/claude/windleblo-archive/windleblo-complete-archive/blog")
    output_dir = Path("/Users/x25bd/Code/windleblo/blog/_posts")
    output_dir.mkdir(exist_ok=True)
    
    # Find all HTML files
    html_files = list(archive_dir.rglob("*.html"))
    print(f"Found {len(html_files)} HTML files")
    
    # Process first 5 posts as a test
    success_count = 0
    for html_file in html_files[:5]:
        print(f"\nProcessing: {html_file}")
        try:
            post_data = extract_post(html_file)
            if create_jekyll_post(post_data, output_dir):
                success_count += 1
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
    
    print(f"\nSuccessfully extracted {success_count} posts")


if __name__ == "__main__":
    main()