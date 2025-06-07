FROM python:3.11-slim

ARG UID=1001
ARG GID=1001

RUN apt update && \
    apt install -y sudo && \
    addgroup --gid $GID nippy && \
    adduser --uid $UID --gid $GID --disabled-password --gecos "" nippy && \
    echo 'nippy ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    libmagic-dev \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/nippy/src

COPY ./src /opt/nippy/src

RUN chown nippy /opt/nippy

RUN pip install --no-cache-dir -r requirements.txt

USER nippy

RUN mkdir /opt/nippy/public