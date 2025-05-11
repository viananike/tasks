FROM python:3.9-slim

# Install system dependencies for building packages
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    libffi-dev \
    make \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \ 
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app
COPY . .

# Expose the port your app runs on
EXPOSE 5000

# Command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

