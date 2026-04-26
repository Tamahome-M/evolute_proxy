FROM python:3.11-slim

RUN pip install --upgrade pip

RUN pip install flask requests

WORKDIR /

COPY . .

EXPOSE ${PORT}
RUN chmod +x /run.sh
CMD /run.sh
