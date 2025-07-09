# Windleblo Blog

Rebuilt version of windleblo.com using Jekyll and GitHub Pages.

## Overview

This is the source code for the Windleblo sailing blog, rebuilt from Wayback Machine archives to maintain the exact URL structure and content while providing a modern, maintainable platform.

## Features

- **Jekyll static site generator** - Fast, secure, and GitHub Pages compatible
- **Decap CMS** - WordPress-like admin interface at `/admin`
- **Original URL structure** - All historical links preserved: `/blog/YYYY/MM/DD/post-slug/`
- **106 historical posts** - Extracted from 2015-2024 archives
- **Responsive design** - Clean, readable on all devices
- **GitHub Actions** - Automatic deployment on push

## Setup

### Prerequisites
- Ruby 3.2+
- Bundler
- Git

### Local Development
```bash
bundle install
bundle exec jekyll serve
```

Visit `http://localhost:4000` to view the site.

### Content Management
Visit `/admin` to access the CMS interface for creating and editing posts.

## Deployment

The site automatically deploys to GitHub Pages when changes are pushed to the main branch.

## File Structure

```
├── _posts/          # Blog posts in Markdown
├── _layouts/        # Page templates
├── assets/          # CSS, images, etc.
├── admin/           # Decap CMS configuration
├── _config.yml      # Jekyll configuration
└── README.md        # This file
```

## Content Migration

All 106 historical posts have been extracted from Wayback Machine archives and converted to Markdown format. The extraction preserved:
- Original publication dates
- Post titles and content
- URL structure
- Image references (images need to be downloaded separately)

## Contributing

1. Make changes locally
2. Test with `bundle exec jekyll serve`
3. Commit with descriptive messages
4. Push to main branch for automatic deployment

## License

Content is owned by the author. Code is available under MIT license.