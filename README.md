# PriceComp

PriceComp is a scraper engine and API that retrieves product data from several Australian music retailers and serves them via REST.

## Getting Started

```bash
# Install dependencies via pipenv (Python 3.9 recommended)
pipenv install

# Set up SQLite DB
pipenv run prisma db push

# Copy and fill out the .env_template
cp .env_template .env

# Run the API
pipenv run dev

# Or run an individual scraper via the cli
pipenv run cli <scraper>
```
## Usage

Most requests require an API key. To get one, make a POST request to `/api/auth/new?admin_key=` and use the `ADMIN_KEY` as a query param (this is set in `.env`).

Auto-generated docs can be found at `/docs`.

## Deployment

As PriceComp currently only uses SQLite, a simple `docker compose up -d` should work fine :)