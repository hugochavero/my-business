FROM python:3.10.1-slim-buster
RUN apt update && apt install --yes git gcc libcurl4-openssl-dev libssl-dev

ENV PYTHONPATH=business

RUN pip3 install poetry

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction
RUN git config --global --add safe.directory /app

COPY . /app
CMD poetry run gunicorn --workers=2 --bind 0.0.0.0:8000 video_engine.wsgi