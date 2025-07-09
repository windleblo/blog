# Windleblo Blog - Developer Setup & Configuration

## Tech Stack Overview

### Core Technologies
- **Jekyll 4.3** - Static site generator
- **Decap CMS** - Git-based content management system
- **Netlify** - Hosting and deployment platform
- **GitHub** - Code repository and version control

### Key Features
- Automatic deployment from GitHub pushes
- WordPress-like admin interface at `/admin`
- Preserved URL structure from original site
- Responsive design with custom styling
- RSS feed generation

## Local Development

### Prerequisites
- Ruby 3.2.2 (specified in `.ruby-version`)
- Docker (recommended for consistent environment)

### Running Locally

#### Option 1: Docker (Recommended)
```bash
make serve
# or
docker-compose up --build
```
Visit: http://localhost:4000

#### Option 2: Native Ruby
```bash
bundle install
bundle exec jekyll serve
```

### Development Commands
```bash
make serve    # Start development server
make build    # Build for production
make clean    # Clean generated files
make stop     # Stop Docker containers
```

## Deployment Architecture

### Netlify Configuration
- **Build command**: `bundle exec jekyll build`
- **Publish directory**: `_site`
- **Ruby version**: 3.2.2 (configured in `netlify.toml`)

### Content Management
- **CMS Backend**: `git-gateway` (Netlify Identity + GitHub)
- **Authentication**: Netlify Identity
- **Content Storage**: GitHub repository (`_posts/` directory)
- **Media Storage**: `assets/images/` directory

## File Structure

```
blog/
├── _posts/              # Blog posts (106 historical posts)
├── _layouts/            # Jekyll templates
├── _config.yml          # Jekyll configuration
├── admin/               # Decap CMS configuration
│   ├── config.yml       # CMS field definitions
│   └── index.html       # CMS admin interface
├── assets/
│   ├── css/
│   │   ├── style.css    # Base styles
│   │   └── custom.css   # Custom windleblo styles
│   └── images/          # Media uploads
├── docs/                # Documentation
├── Gemfile              # Ruby dependencies
├── netlify.toml         # Netlify build settings
└── docker-compose.yml   # Local development setup
```

## Content Management System

### Admin Interface
- **URL**: https://[site-name].netlify.app/admin
- **Authentication**: Netlify Identity
- **Capabilities**: Create/edit posts, manage pages, upload images

### Post Creation Flow
1. User writes post in admin interface
2. CMS generates markdown file in `_posts/`
3. Git commit triggered via Netlify Git Gateway
4. Netlify automatically rebuilds and deploys site

## Customizations

### URL Structure
- **Posts**: `/blog/YYYY/MM/DD/post-slug/`
- **Pages**: `/page-name/`
- **Feed**: `/feed.xml`

### Styling
- Base theme: Modified minima
- Custom CSS: `assets/css/custom.css`
- Responsive design with wider content margins
- Full-width header with proper alignment

### Historical Content
- 106 posts extracted from Wayback Machine archives
- Content preserved from 2015-2024
- Image references maintained (images need separate hosting)

## Maintenance

### Adding New Features
1. Make changes locally
2. Test with `make serve`
3. Commit and push to GitHub
4. Netlify automatically deploys

### Troubleshooting
- **Build failures**: Check Ruby version compatibility
- **CMS issues**: Verify Netlify Identity and Git Gateway are enabled
- **Styling problems**: Check CSS file loading order

### Dependencies
- Ruby gems managed via Bundler
- Jekyll plugins: feed, SEO, sitemap
- Node.js not required (pure Jekyll setup)

## Security Notes
- All authentication handled by Netlify Identity
- No sensitive credentials in repository
- HTTPS enforced by Netlify
- Admin access controlled via email invitations

## Backup Strategy
- Primary: GitHub repository
- Secondary: Netlify keeps build artifacts
- Content: All posts stored as markdown files in Git