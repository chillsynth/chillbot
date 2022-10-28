FROM python:alpine
RUN pip install discord.py[voice]
WORKDIR /chillbot
COPY /bot/ /chillbot/
