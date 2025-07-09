#!/usr/bin/env python3
"""
Extract blog content from Wayback Machine HTML archives - Version 2
"""

import os
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import html2text

def extract_post(html_file):
    """Extract post data from HTML file"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title
    title_elem = soup.find('h1', class_='entry-title')
    title = title_elem.get_text(strip=True) if title_elem else ''
    
    # Extract date
    date_elem = soup.find('time', class_='entry-date')
    date = date_elem.get('datetime', '') if date_elem else ''
    
    # Extract content
    content_elem = soup.find('div', class_='entry-content')
    
    if content_elem:
        # Remove navigation and footer content
        for nav in content_elem.find_all('nav'):
            nav.decompose()
        for footer in content_elem.find_all('footer'):
            footer.decompose()
        
        # Clean up image URLs
        for img in content_elem.find_all('img'):
            src = img.get('src', '')
            # Remove wayback machine prefix
            src = re.sub(r'https://web\.archive\.org/web/\d+im_/', '', src)
            img['src'] = src
        
        # Convert to markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # Don't wrap lines
        content_text = h.handle(str(content_elem))
        
        # Clean up the content
        content_text = re.sub(r'\n{3,}', '\n\n', content_text)
        content_text = content_text.strip()
    else:
        content_text = ""
    
    # Extract date from file path if not found
    if not date:
        match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', str(html_file))
        if match:
            date = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    
    # Extract slug from file path
    slug = Path(html_file).stem
    
    return {
        'title': title or slug.replace('-', ' ').title(),
        'date': date,
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
    html_files = sorted(list(archive_dir.rglob("*.html")))
    print(f"Found {len(html_files)} HTML files")
    
    # Process all posts
    success_count = 0
    for i, html_file in enumerate(html_files):
        print(f"\nProcessing {i+1}/{len(html_files)}: {html_file.name}")
        try:
            post_data = extract_post(html_file)
            if create_jekyll_post(post_data, output_dir):
                success_count += 1
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
    
    print(f"\nSuccessfully extracted {success_count} posts")


if __name__ == "__main__":
    main()