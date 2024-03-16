FROM python:slim-bookworm

WORKDIR /chillbot
COPY ./ /chillbot/

RUN apt install tzdata
RUN pip install -r requirements.txt

CMD ["python", "-u", "bot"]
