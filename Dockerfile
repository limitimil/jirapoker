COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./app /app
WORKDIR /app

ENV PYTHONPATH=/app


CMD ["python3", "/app/main.py"]