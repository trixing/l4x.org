FROM debian:stretch

MAINTAINER Jan Dittmer <jdi@l4x.org>
# Build: docker build -t trixing/l4x.org .
# Run: docker run -p 8007:8007 trixing/l4x.org

ENV TZ=
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

EXPOSE 8007

RUN apt-get update && apt-get -y install python-gevent pyblosxom bash vim locales python-bibtex python-docutils python-markdown

COPY . /app

CMD ["/usr/bin/python", "/app/pyblosxom_gevent.py"]
