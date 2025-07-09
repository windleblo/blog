#!/usr/bin/env python3
"""
Test the migration script on a small sample
"""

from migrate_blogspot import BlogspotMigrator
import sys

def test_migration():
    migrator = BlogspotMigrator()
    
    # Test fetching sitemap
    print("Testing sitemap fetch...")
    urls = migrator.get_sitemap_urls()
    
    if not urls:
        print("ERROR: No URLs found!")
        return False
    
    print(f"Found {len(urls)} total URLs")
    print("Sample URLs:")
    for i, url in enumerate(urls[:5]):
        print(f"  {i+1}. {url}")
    
    # Test single post migration
    print("\nTesting single post migration...")
    test_url = urls[0]  # Use the first URL
    
    # Extract date
    post_date = migrator.extract_post_date(test_url)
    print(f"Extracted date: {post_date}")
    
    # Fetch content
    post_data = migrator.fetch_post_content(test_url)
    if post_data:
        print(f"Title: {post_data['title']}")
        print(f"Content length: {len(post_data['content'])} characters")
        print(f"Content preview: {post_data['content'][:200]}...")
        
        # Test markdown conversion
        markdown = migrator.convert_to_markdown(post_data['content'])
        print(f"Markdown length: {len(markdown)} characters")
        print(f"Markdown preview: {markdown[:200]}...")
        
        # Test Jekyll post creation
        success = migrator.create_jekyll_post(post_data, post_date)
        print(f"Jekyll post created: {success}")
        
    else:
        print("ERROR: Could not fetch post content!")
        return False
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    test_migration()