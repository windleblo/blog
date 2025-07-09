#!/usr/bin/env python3
"""
Debug the content extraction
"""

import requests
import re

def debug_extraction():
    url = "https://windleblo.blogspot.com/2010/04/spring-has-sprung.html"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    response = session.get(url)
    html_content = response.text
    
    print(f"HTML content length: {len(html_content)}")
    
    # Look for different patterns
    patterns = [
        r'<div class="post-body entry-content"[^>]*>(.*?)</div>',
        r'<div class="post-body"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*post-body[^"]*"[^>]*>(.*?)</div>',
        r'<div class="entry-content"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*entry-content[^"]*"[^>]*>(.*?)</div>',
        r'<div class="post"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*post[^"]*"[^>]*>(.*?)</div>',
    ]
    
    print("\nTesting patterns:")
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1)
            print(f"Pattern {i+1} MATCHED: {len(content)} chars")
            print(f"Content preview: {content[:200]}...")
            break
        else:
            print(f"Pattern {i+1} failed")
    
    # Look for any div with "post" in the class
    post_divs = re.findall(r'<div[^>]*class="[^"]*post[^"]*"[^>]*>', html_content, re.IGNORECASE)
    print(f"\nFound {len(post_divs)} divs with 'post' in class:")
    for div in post_divs[:5]:
        print(f"  {div}")
    
    # Search for actual content keywords
    if "Spring has sprung" in html_content:
        print("\nFound 'Spring has sprung' in HTML")
        # Find the context around this text
        start = html_content.find("Spring has sprung") - 200
        end = html_content.find("Spring has sprung") + 500
        context = html_content[max(0, start):end]
        print(f"Context: {context}")
        
        # Look for the actual post content after meta tags
        post_content_start = html_content.find("Spring has sprung", html_content.find("</head>"))
        if post_content_start > 0:
            post_section = html_content[post_content_start-100:post_content_start+1000]
            print(f"\nPost section: {post_section}")
    else:
        print("\nDid not find 'Spring has sprung' in HTML")
        
    # Try a different approach - look for itemprop="description" or "articleBody"
    description_match = re.search(r'<div[^>]*itemprop="description"[^>]*>(.*?)</div>', html_content, re.DOTALL | re.IGNORECASE)
    if description_match:
        print(f"\nFound description: {description_match.group(1)[:200]}...")
    
    articleBody_match = re.search(r'<div[^>]*itemprop="articleBody"[^>]*>(.*?)</div>', html_content, re.DOTALL | re.IGNORECASE)
    if articleBody_match:
        print(f"\nFound articleBody: {articleBody_match.group(1)[:200]}...")

if __name__ == "__main__":
    debug_extraction()