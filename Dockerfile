FROM python
RUN pip install discord.py[voice]
RUN git clone https://github.com/npgy/chillbot