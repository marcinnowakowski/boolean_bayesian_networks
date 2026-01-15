# Use an official Python 2 runtime as a parent image
FROM python:2.7-slim

# Set the working directory to /app
WORKDIR /app

# FIX: Debian Buster is EOL, so we must switch to archive.debian.org
# We also disable the "Valid-Until" check because archived release files are expired.
RUN echo "deb http://archive.debian.org/debian buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list && \
    apt-get -o Acquire::Check-Valid-Until=false update && \
    apt-get -o Acquire::Check-Valid-Until=false install -y \
    gcc \
    g++ \
    python-dev \
    libblas-dev \
    liblapack-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install BNFinder2 directly from PyPI
RUN pip install --no-cache-dir BNFinder

# Create a volume mount point for input/output data
VOLUME /data

# Set the default command to show help
CMD ["bnf", "--help"]