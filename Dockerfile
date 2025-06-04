ARG url_docker=docker.io
ARG url_pypi=https://pypi.org/simple/
FROM ${url_docker}/python:3.13.3-bookworm

ARG url_pypi
ENV url_pypi=${url_pypi}

WORKDIR /opt/partyapp
COPY ./main/ ./
COPY requirements.prod.txt ./
COPY init_app.py ./

RUN mkdir -p /var/log/partyapp
RUN mkdir -p /var/cache/partyapp
RUN pip install -r ./requirements.prod.txt --index-url ${url_pypi}