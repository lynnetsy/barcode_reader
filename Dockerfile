FROM python:3.9-slim

WORKDIR /app

# Instala las dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libtiff-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk2.0-dev \
    libatlas-base-dev \
    gfortran \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libzbar0 \
    libzbar-dev \
    poppler-utils \ 
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["tail", "-f", "/dev/null"]
