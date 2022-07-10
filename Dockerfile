FROM python:3.10.4-buster
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

RUN pip install yt-dlp
RUN pip install selenium
COPY code .

CMD ["python3", "main.py"]