# Windleblo Blog Rebuild Project

## Project Overview
Rebuilding windleblo.com blog from wayback machine archives using Jekyll and GitHub Pages.

## Key Requirements
- Preserve exact URL structure: `/blog/YYYY/MM/DD/post-slug/`
- Maintain all historical content from 2015-2024
- Simple, clean design with photo support
- Decap CMS for WordPress-like admin interface
- GitHub Pages hosting with custom domain

## Development Instructions
1. **Make regular, well-described commits** - Commit changes frequently with clear, descriptive messages
2. **Test locally before pushing** - Always run `bundle exec jekyll serve` to verify changes
3. **Preserve URL structure** - Critical for maintaining old links
4. **Extract content carefully** - Ensure dates, titles, and content are accurately preserved

## Tech Stack
- **Jekyll**: Static site generator
- **Decap CMS**: Git-based content management
- **GitHub Pages**: Hosting
- **Ruby/Bundler**: Development dependencies

## Content Location
Original HTML archives: `/Users/x25bd/Code/windleblo/claude/windleblo-archive/windleblo-complete-archive/blog/`

## Commit Guidelines
- Use descriptive commit messages
- Commit after each major step
- Group related changes together
- Example: "Add Jekyll configuration with permalink structure"