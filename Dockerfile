FROM ubuntu:16.04

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./app /app
WORKDIR /app

ENV PYTHONPATH=/app


CMD ["python3", "/app/main.py"]