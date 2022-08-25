# Contributing

## Dependencies
- Python >=3.9
- [Poetry](https://python-poetry.org/docs/master/#installing-with-the-official-installer)

## Setup
* Install Python dependencies with poetry
```shell
poetry install
```

- Set up the database
```shell
poetry run python manage.py migrate
```

- Start the API server
```shell
poetry run python manage.py runserver
```

### Updating the database

If you modify any database models (`models.py`), you'll need to run the following to update the database:
```shell
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```

### Linting

```shell
poetry run mypy
poetry run black .
```
