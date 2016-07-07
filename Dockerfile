FROM hivesolutions/pypy:latest
MAINTAINER Hive Solutions

EXPOSE 8080

ENV LEVEL INFO
ENV SERVER netius
ENV SERVER_ENCODING gzip
ENV HOST 0.0.0.0
ENV PORT 8080
ENV MONGOHQ_URL mongodb://localhost:27017

ADD requirements.txt /
ADD extra.txt /
ADD src /src

RUN pip install -r /requirements.txt && pip install -r /extra.txt && pip install --upgrade netius

CMD ["/usr/bin/python", "/src/story/main.py"]
