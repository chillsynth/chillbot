FROM python:alpine

WORKDIR /chillbot
COPY ./ /chillbot/

RUN pip install -r requirements.txt

CMD ["python", "bot"]
