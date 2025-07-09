#!/usr/bin/env python3
"""
Test the enhanced migration script on a small sample
"""

from migrate_blogspot import BlogspotMigrator

def test_enhanced_migration():
    migrator = BlogspotMigrator()
    
    # Get all URLs
    urls = migrator.get_sitemap_urls()
    
    if not urls:
        print("No URLs found")
        return
    
    # Test with posts that are likely to have images
    test_urls = [
        'https://windleblo.blogspot.com/2013/04/sicily.html',  # Known to have images
        'https://windleblo.blogspot.com/2010/04/spring-has-sprung.html',  # First post
        'https://windleblo.blogspot.com/2013/05/2013-cruising-plan.html'  # Another post
    ]
    
    print(f"Testing enhanced migration with {len(test_urls)} posts...")
    
    successful = 0
    failed = 0
    
    for url in test_urls:
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
        
        # Create Jekyll post (with image and link processing)
        if migrator.create_jekyll_post(post_data, better_date):
            successful += 1
        else:
            failed += 1
    
    # Generate redirects
    migrator.generate_redirects()
    
    print(f"\nEnhanced migration test complete: {successful} successful, {failed} failed")
    print(f"Downloaded {len(migrator.downloaded_images)} images")
    print(f"Generated {len(migrator.redirects)} redirects")

if __name__ == "__main__":
    test_enhanced_migration()