# Use Python 3.12 as the base image
FROM python:3.12-slim


# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages and run setup script
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install poetry && \
    chmod +x ./setup.sh && \
    ./setup.sh


# Run the miner when the container launches
CMD ["./bin/volara", "mine", "start"]
