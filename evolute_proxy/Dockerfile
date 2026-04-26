FROM python:3.11-slim

RUN apk add --no-cache python3 py3-pip bash
RUN pip3 install --no-cache-dir flask requests

COPY run.sh /run.sh
COPY evolute_api.py /evolute_api.py
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
