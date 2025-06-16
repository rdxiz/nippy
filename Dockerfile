FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    libmagic-dev \
    ffmpeg \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/nippy/src

COPY ./src /opt/nippy/src

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /opt/nippy/public/static

RUN npm install

RUN npm run build
