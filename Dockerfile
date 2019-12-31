FROM python:3.6

COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./app /app
WORKDIR /app

ENV PYTHONPATH=/app


CMD ["python", "/app/main.py"]