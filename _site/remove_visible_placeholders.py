#!/usr/bin/env python3
"""
Remove visible image placeholders from all posts while keeping HTML comments
"""

import os
import re
from pathlib import Path

def remove_visible_placeholders(content):
    """Remove visible image placeholders but keep HTML comments"""
    
    # Pattern to match the visible placeholder and filename line
    pattern = r'\*\*\[IMAGE MISSING: [^\]]*\]\*\*\n\*Original filename: [^\n]*\*\n\n?'
    
    # Remove the visible placeholders
    content = re.sub(pattern, '', content)
    
    return content

def process_post(file_path):
    """Process a single post file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    content = remove_visible_placeholders(content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {file_path}")
        return True
    
    return False

def main():
    posts_dir = Path('_posts')
    
    if not posts_dir.exists():
        print("Posts directory not found!")
        return
    
    updated_count = 0
    
    for post_file in posts_dir.glob('*.md'):
        if process_post(post_file):
            updated_count += 1
    
    print(f"\nProcessed {updated_count} posts")

if __name__ == '__main__':
    main()