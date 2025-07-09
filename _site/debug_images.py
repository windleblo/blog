#!/usr/bin/env python3
"""
Debug image extraction
"""

from migrate_blogspot import BlogspotMigrator
import re

def debug_images():
    migrator = BlogspotMigrator()
    url = 'https://windleblo.blogspot.com/2013/04/sicily.html'
    
    # Fetch content
    post_data = migrator.fetch_post_content(url)
    if not post_data:
        print("Failed to fetch post")
        return
    
    print(f"Title: {post_data['title']}")
    print(f"Content length: {len(post_data['raw_content'])}")
    
    # Look for images in raw content
    content = post_data['raw_content']
    img_pattern = r'<img[^>]*src=["\']([^"\']*)["\'][^>]*>'
    images = re.findall(img_pattern, content, re.IGNORECASE)
    
    print(f"Found {len(images)} images in extracted content:")
    for i, img_url in enumerate(images):
        print(f"  {i+1}. {img_url}")
    
    # Also check full HTML content
    full_html = post_data['html_content']
    full_images = re.findall(img_pattern, full_html, re.IGNORECASE)
    
    print(f"\nFound {len(full_images)} images in full HTML:")
    for i, img_url in enumerate(full_images):
        print(f"  {i+1}. {img_url}")
    
    # Check if content contains obvious image indicators
    if 'img' in content.lower():
        print("\n'img' found in extracted content")
    if 'img' in full_html.lower():
        print("'img' found in full HTML")
    if 'photobucket' in full_html.lower():
        print("'photobucket' found in full HTML")
    if 'googleusercontent' in full_html.lower():
        print("'googleusercontent' found in full HTML")
    
    # Show a sample of the content
    print(f"\nExtracted content sample (first 500 chars):\n{content[:500]}")
    
    # Look for where images might be in the full HTML
    if 'img' in full_html.lower():
        img_pos = full_html.lower().find('img')
        print(f"\nFirst 'img' found at position {img_pos}")
        print(f"Context around first image:\n{full_html[max(0,img_pos-100):img_pos+200]}")

if __name__ == "__main__":
    debug_images()