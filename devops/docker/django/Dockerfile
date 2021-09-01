ARG IMAGE=python:latest
FROM $IMAGE

RUN apt-get update && apt-get -y dist-upgrade
RUN apt-get install -y netcat

ENV PIPENV_DONT_LOAD_ENV=1
ENV PIPENV_KEEP_OUTDATED=1
ENV PY_COLORS=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN pip install pipenv
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --dev --deploy
COPY . /app/
