FROM python:alpine

WORKDIR /chillbot
COPY ./ /chillbot/

RUN apk add tzdata
RUN pip install -r requirements.txt

CMD ["python", "-u", "bot"]
