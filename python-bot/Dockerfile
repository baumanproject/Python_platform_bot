FROM python:3.6-alpine

RUN apk add --no-cache \
  uwsgi \
  uwsgi-python3 \
  gcc musl-dev

RUN pip install virtualenv

RUN virtualenv /venv

RUN /venv/bin/pip install flask telepot web3 emoji flask_sqlalchemy pymongo telethon

RUN mkdir /app/
ADD *.py /app/
ADD uwsgi.ini /app/

EXPOSE 5555

ENTRYPOINT ["/usr/sbin/uwsgi", "--plugin", "python3", "--ini", "/app/uwsgi.ini", "-s", "0.0.0.0:5555"]
