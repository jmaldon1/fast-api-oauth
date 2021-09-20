# fast-api-oauth

Example oauth with fast-api

# Installation

## Poetry

Install [Poetry](https://python-poetry.org/)

## Install dependencies

```
poetry install
```

# API Server

## Run server

   Run server with:

   ```sh
   poetry run uvicorn oauth_app.main:app --reload
   ```

## API

Available at: http://localhost:8000/

## OpenAPI docs

Visit http://localhost:8000/docs#/

# Database

## Start the database

Start the database with:

```sh
docker-compose up
```

## Initialize Database

To initialize the database with migrations and a superuser run:

```sh
python run_init_db.py
```

# Migrations

## 1. Make changes to models or add new models

* If changes were made to existing models:
   1. Create a new revision with:
      ```sh
      alembic revision --autogenerate -m "Updated model"
      ```

* If a new model was added:
   1. Import it into `oauth_app.app.database.base`
   2. Create a new revision with:
      ```sh
      alembic revision --autogenerate -m "New model"
      ```

## 2. Commit changes to database

Commit the new revisions to the database with:

```sh
alembic upgrade head
```

# Tests

## Requirements

Must have `docker` and `docker-compose` installed

## Run tests

Run tests with:

```sh
pytest -s -v
```