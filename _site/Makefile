# Windleblo Blog Development Commands

.PHONY: serve build clean install

# Serve the blog locally with Docker
serve:
	docker-compose up --build

# Build the site for production
build:
	docker-compose run --rm blog bundle exec jekyll build

# Clean generated files
clean:
	docker-compose run --rm blog bundle exec jekyll clean
	docker-compose down -v

# Install dependencies
install:
	docker-compose run --rm blog bundle install

# One-time setup
setup:
	docker-compose build
	docker-compose run --rm blog bundle install

# Stop the server
stop:
	docker-compose down