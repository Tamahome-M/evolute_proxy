FROM python:3.11-slim

RUN pip install --upgrade pip

RUN pip install flask requests

WORKDIR /

COPY run.sh /run.sh
COPY evolute_api.py /evolute_api.py


EXPOSE ${PORT}
RUN chmod +x /run.sh
CMD /run.sh
