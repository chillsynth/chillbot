FROM python:3.11.1-slim
WORKDIR /chillbot
COPY /bot/ /chillbot/
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD ["python3", "__main__.py"]