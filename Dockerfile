FROM python:alpine
RUN pip install discord.py[voice]
RUN wget https://github.com/npgy/chillbot/archive/refs/heads/docker.zip && unzip docker.zip -d temp && mkdir chillbot && mv temp/chillbot-docker/** chillbot/ && rm docker.zip && rm -rf temp
