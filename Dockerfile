FROM python:3.9
ADD quotebot.py .
ADD requirements.txt .
RUN apt-get install ffmpeg
RUN pip install -r requirements.txt

CMD python quotebot.py