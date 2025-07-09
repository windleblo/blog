#!/usr/bin/env python3
"""
Fix content formatting issues in extracted posts
"""

import os
import re
from pathlib import Path

def fix_headers(content):
    """Convert text headers to proper markdown headers"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip if line is empty or already a header
        if not line.strip() or line.strip().startswith('#'):
            fixed_lines.append(line)
            continue
            
        # Look for standalone lines that might be headers
        # - Short lines (under 60 chars)
        # - Not part of a paragraph (surrounded by empty lines)
        # - Don't contain common paragraph words
        if (len(line.strip()) < 60 and 
            line.strip() and 
            not line.strip().endswith('.') and
            not line.strip().endswith(',') and
            not line.strip().endswith(':') and
            not line.strip().startswith('![') and
            not line.strip().startswith('http') and
            not line.strip().startswith('*')):
            
            # Check if surrounded by empty lines or at start/end
            prev_empty = i == 0 or not lines[i-1].strip()
            next_empty = i == len(lines)-1 or not lines[i+1].strip()
            
            if prev_empty and next_empty:
                # This looks like a header
                fixed_lines.append(f"## {line.strip()}")
                continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_images(content):
    """Convert broken image references to placeholders with metadata"""
    
    # Pattern to match: ![](url)Caption text
    image_pattern = r'!\[\]\((http://windleblo\.com/wp-content/uploads/[^)]+)\)([^\n]*)'
    
    def replace_image(match):
        url = match.group(1)
        caption = match.group(2).strip()
        
        # Extract metadata from URL
        filename = url.split('/')[-1]
        date_path = '/'.join(url.split('/')[5:8])  # Extract YYYY/MM
        
        # Create placeholder with metadata
        placeholder = f'''
<!-- IMAGE PLACEHOLDER
Original URL: {url}
Filename: {filename}
Date path: {date_path}
Caption: {caption}
Instructions: Replace this comment with actual image upload
-->

**[IMAGE MISSING: {caption}]**
*Original filename: {filename}*
'''
        return placeholder.strip()
    
    return re.sub(image_pattern, replace_image, content)

def clean_content(content):
    """Clean up various content issues"""
    
    # Remove excessive whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Fix quote formatting
    content = re.sub(r'^"([^"]+)"$', r'> "\1"', content, flags=re.MULTILINE)
    
    # Fix common punctuation issues
    content = content.replace('"', '"').replace('"', '"')
    content = content.replace(''', "'").replace(''', "'")
    
    return content.strip()

def process_post(file_path):
    """Process a single post file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split front matter and content
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"Warning: No front matter found in {file_path}")
        return False
    
    front_matter = parts[1]
    body_content = parts[2]
    
    # Apply fixes
    body_content = fix_headers(body_content)
    body_content = fix_images(body_content)
    body_content = clean_content(body_content)
    
    # Reassemble
    fixed_content = f"---{front_matter}---\n\n{body_content}"
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    return True

def main():
    posts_dir = Path("_posts")
    
    if not posts_dir.exists():
        print("Error: _posts directory not found")
        return
    
    post_files = list(posts_dir.glob("*.md"))
    print(f"Found {len(post_files)} posts to process")
    
    success_count = 0
    for post_file in post_files:
        print(f"Processing: {post_file.name}")
        try:
            if process_post(post_file):
                success_count += 1
        except Exception as e:
            print(f"Error processing {post_file}: {e}")
    
    print(f"\nSuccessfully processed {success_count}/{len(post_files)} posts")
    
    # Show example of what changed
    print("\nExample changes:")
    print("- Headers: 'Section Title' → '## Section Title'")
    print("- Images: ![](broken-url)Caption → [IMAGE MISSING: Caption] with metadata")
    print("- Comments added with original filenames for re-uploading")

if __name__ == "__main__":
    main()