#!/usr/bin/env python3
"""
Simple development server to preview the blog locally
"""

import http.server
import socketserver
import os
import markdown
import re
from pathlib import Path
from datetime import datetime

class BlogHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle blog post URLs
        if self.path.startswith('/blog/'):
            # Extract year, month, day, slug from path
            match = re.match(r'/blog/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?', self.path)
            if match:
                year, month, day, slug = match.groups()
                post_file = f"_posts/{year}-{month}-{day}-{slug}.md"
                
                if os.path.exists(post_file):
                    self.serve_post(post_file)
                    return
        
        # Handle root path
        if self.path == '/':
            self.serve_home()
            return
            
        # Handle static files
        super().do_GET()
    
    def serve_post(self, post_file):
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract front matter
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front_matter = parts[1]
            body = parts[2]
        else:
            front_matter = ""
            body = content
        
        # Parse front matter
        title = "Windleblo"
        date = ""
        for line in front_matter.split('\n'):
            if line.startswith('title:'):
                title = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('date:'):
                date = line.split(':', 1)[1].strip()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(body)
        
        # Generate HTML page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title} - Windleblo</title>
            <style>
                body {{ font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .post-meta {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
                img {{ max-width: 100%; height: auto; }}
                a {{ color: #0066cc; }}
            </style>
        </head>
        <body>
            <nav><a href="/">← Back to Home</a></nav>
            <h1>{title}</h1>
            <div class="post-meta">{date}</div>
            <div class="post-content">{html_content}</div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_home(self):
        # List all posts
        posts = []
        for post_file in sorted(Path('_posts').glob('*.md'), reverse=True):
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract front matter
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter = parts[1]
                
                title = post_file.stem
                date = ""
                for line in front_matter.split('\n'):
                    if line.startswith('title:'):
                        title = line.split(':', 1)[1].strip().strip('"')
                    elif line.startswith('date:'):
                        date = line.split(':', 1)[1].strip()
                
                # Generate URL
                name_parts = post_file.stem.split('-', 3)
                if len(name_parts) >= 4:
                    year, month, day, slug = name_parts
                    url = f"/blog/{year}/{month}/{day}/{slug}/"
                    posts.append({'title': title, 'date': date, 'url': url})
        
        # Generate HTML
        post_list = ""
        for post in posts[:10]:  # Show first 10 posts
            post_list += f'<li><a href="{post["url"]}">{post["title"]}</a> - {post["date"]}</li>'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Windleblo - Sailing Blog</title>
            <style>
                body {{ font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .tagline {{ color: #666; font-style: italic; margin-bottom: 30px; }}
                ul {{ list-style: none; padding: 0; }}
                li {{ margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #eee; }}
                a {{ color: #0066cc; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Windleblo</h1>
            <p class="tagline">The cruising blog for S/V Windleblo, a Hallberg-Rassy 40</p>
            <h2>Recent Posts</h2>
            <ul>{post_list}</ul>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

def main():
    PORT = 8000
    
    with socketserver.TCPServer(("", PORT), BlogHandler) as httpd:
        print(f"Blog server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    main()