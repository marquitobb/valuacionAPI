FROM python:3.8.5-slim-buster

WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./docker/services/web/requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./src/ /usr/src/app