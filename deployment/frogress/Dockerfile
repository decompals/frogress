FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl netcat

ARG POETRY_VERSION=1.1.15
ENV POETRY_VERSION=${POETRY_VERSION}
RUN curl -sSL https://install.python-poetry.org | \
    POETRY_VERSION=${POETRY_VERSION} POETRY_HOME=/etc/poetry python -

RUN echo 'export PATH="/etc/poetry/bin:$PATH"' > /root/.bashrc

RUN mkdir /frogress

COPY consumer_scripts /frogress/consumer_scripts
COPY frog_api /frogress/frog_api
COPY frogress /frogress/frogress

COPY manage.py /frogress/
COPY mypy.ini /frogress/
COPY poetry.lock /frogress/
COPY pyproject.toml /frogress/

COPY ./deployment/frogress/entrypoint.sh /entrypoint.sh

WORKDIR /frogress

ENV PATH="$PATH:/etc/poetry/bin"

RUN poetry install

COPY .env /frogress

ENTRYPOINT ["/entrypoint.sh"]