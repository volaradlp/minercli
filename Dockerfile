# Use Python 3.12 as the base image
FROM python:3.12-slim


# Install any needed packages and run setup script
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
# COPY . /app
RUN git clone https://github.com/volaradlp/minercli.git /app

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install

# Run git pull and start the miner when the container launches
CMD git pull origin main && ./bin/volara mine start
