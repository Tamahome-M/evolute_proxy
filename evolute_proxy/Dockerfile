FROM python:3.11-slim

RUN pip install --upgrade pip

RUN pip install flask requests

WORKDIR /

COPY . .

EXPOSE ${PORT}

CMD /run.sh
