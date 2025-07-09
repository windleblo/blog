#!/usr/bin/env python3
"""
Run migration on first 10 posts for testing
"""

from migrate_blogspot import BlogspotMigrator

def migrate_sample():
    migrator = BlogspotMigrator()
    
    # Get all URLs
    urls = migrator.get_sitemap_urls()
    
    if not urls:
        print("No URLs found")
        return
    
    # Take first 10 URLs
    sample_urls = urls[:10]
    
    print(f"Migrating first {len(sample_urls)} posts...")
    
    successful = 0
    failed = 0
    
    for url in sample_urls:
        print(f"\n--- Processing {url} ---")
        
        # Extract date from URL
        post_date = migrator.extract_post_date(url)
        if not post_date:
            print(f"Could not extract date from {url}")
            failed += 1
            continue
        
        # Fetch post content
        post_data = migrator.fetch_post_content(url)
        if not post_data:
            failed += 1
            continue
        
        # Try to get better date from post content
        better_date = migrator.extract_better_date(post_data.get('html_content', ''), post_date)
        print(f"Date: {post_date} -> {better_date}")
        
        # Create Jekyll post
        if migrator.create_jekyll_post(post_data, better_date):
            successful += 1
        else:
            failed += 1
    
    print(f"\nSample migration complete: {successful} successful, {failed} failed")

if __name__ == "__main__":
    migrate_sample()