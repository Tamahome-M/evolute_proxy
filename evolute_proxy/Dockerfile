ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.21
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8

RUN apk add --no-cache \
        python3 \
        py3-pip \
    && pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir flask requests

COPY run.sh /run.sh
COPY evolute_api.py /evolute_api.py

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
