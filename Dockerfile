# Use a base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy your project code
COPY . /app

# Install dependencies (Flask and others from your project)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install Gunicorn (only for Docker setup)
RUN pip install gunicorn

# Expose the port for Flask
EXPOSE 5000

# Default command to run Flask in production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
