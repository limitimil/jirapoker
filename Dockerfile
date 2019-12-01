FROM tiangolo/uwsgi-nginx-flask:python3.7

# Add demo app
COPY ./app /app
WORKDIR /app

#install flask python requirement
COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt
