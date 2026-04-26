FROM python:3.11-slim

RUN pip install --upgrade pip

RUN pip install flask requests

WORKDIR /app

COPY run.sh /run.sh
COPY evolute_api.py /evolute_api.py

RUN chmod +x /run.sh


EXPOSE ${PORT}
RUN ls -l /
RUN cat /run.sh
CMD ["/run.sh"]
