FROM ruby:3.2-alpine

RUN apk add --no-cache \
    build-base \
    git \
    && rm -rf /var/cache/apk/*

WORKDIR /srv/jekyll

COPY Gemfile* ./
RUN bundle install

COPY . .

EXPOSE 4000

CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0"]