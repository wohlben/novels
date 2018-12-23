FROM python:3.6

MAINTAINER bw@wohlben.de

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt
RUN useradd -d /django -m --user-group django

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /bin/wait-for-it
RUN chmod 755 /bin/wait-for-it

USER django
WORKDIR /django

COPY startup.sh startup.sh
COPY app app
COPY novels novels
COPY scrapes scrapes
COPY static static
COPY templates templates
COPY manage.py manage.py

CMD bash startup.sh django
