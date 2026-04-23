ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache py3-pip \
    && pip3 install --no-cache-dir flask requests

COPY evolute_api.py /opt/evolute_api.py
COPY run.sh /run.sh
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
