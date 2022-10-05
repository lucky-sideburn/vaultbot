FROM python:3.8-slim-buster

WORKDIR /app
RUN mkdir /app/conf
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN apt-get clean && apt-get update -y && apt-get install curl -y

COPY . .

CMD [ "python3", "app.py"]
