FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/nippy/src

COPY ./src /opt/nippy/src

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /opt/nippy/public