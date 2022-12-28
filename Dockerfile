FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

WORKDIR /

COPY requirements.txt requirements.txt
COPY run.py run.py
RUN pip install -r requirements.txt

COPY app app

EXPOSE 5000

CMD ["python3", "run.py"]